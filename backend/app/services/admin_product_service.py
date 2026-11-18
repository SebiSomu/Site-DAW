from typing import Sequence

from werkzeug.datastructures import FileStorage

from app.errors import ConflictError, NotFoundError, ValidationError
from app.extensions import db
from app.models import Product, ProductImage
from app.repositories import CategoryRepository, IngredientRepository, ProductImageRepository, ProductRepository
from app.schemas import AdminProductRequest, ImageUploadForm
from app.security.sanitize import plain_text
from app.services.activity_logger import activity_logger
from app.services.slugs import slugify
from app.services.uploads import ImageUploadPipeline, UploadStorage

MAX_IMAGES_PER_PRODUCT = 8
TRACKED_FIELDS = (
    "name",
    "slug",
    "category",
    "description",
    "price_cents",
    "weight_grams",
    "stock",
    "is_active",
    "ingredients",
)


class AdminProductService:
    def __init__(
        self,
        products: ProductRepository | None = None,
        images: ProductImageRepository | None = None,
        categories: CategoryRepository | None = None,
        ingredients: IngredientRepository | None = None,
        pipeline: ImageUploadPipeline | None = None,
    ) -> None:
        self.products = products or ProductRepository()
        self.images = images or ProductImageRepository()
        self.categories = categories or CategoryRepository()
        self.ingredients = ingredients or IngredientRepository()
        self._pipeline = pipeline

    @property
    def pipeline(self) -> ImageUploadPipeline:
        self._pipeline = self._pipeline or ImageUploadPipeline()
        return self._pipeline

    @property
    def storage(self) -> UploadStorage:
        return self.pipeline.storage

    def list_all(self) -> Sequence[Product]:
        return self.products.list_for_admin()

    def get(self, product_id: int) -> Product:
        product = self.products.get_for_admin(product_id)
        if product is None:
            raise NotFoundError("We could not find this jar.")
        return product

    def create(self, data: AdminProductRequest) -> Product:
        product = Product()
        self._apply(product, data)
        self.products.add(product)
        db.session.commit()
        activity_logger.info("product_created", f"product={product.id} slug={product.slug}")
        return self.get(product.id)

    def update(self, product_id: int, data: AdminProductRequest) -> Product:
        product = self.get(product_id)
        before = self._snapshot(product)
        self._apply(product, data)
        changed = [field for field, value in self._snapshot(product).items() if before[field] != value]
        db.session.commit()
        activity_logger.info("product_updated", f"product={product.id} changed={','.join(changed) or 'none'}")
        return self.get(product.id)

    def delete(self, product_id: int) -> None:
        product = self.get(product_id)
        if product.order_items:
            raise ConflictError("This jar is in past orders, so it cannot be deleted. Hide it from the shop instead.")
        filenames = [image.filename for image in product.images]
        slug = product.slug
        self.products.delete(product)
        db.session.commit()
        for filename in filenames:
            self.storage.delete(filename)
        activity_logger.info("product_deleted", f"product={product_id} slug={slug}")

    def add_image(self, product_id: int, form: ImageUploadForm, file: FileStorage | None) -> Product:
        product = self.get(product_id)
        alt_text = self._required_text(form.alt_text, "Describe the photo for people who cannot see it.")
        if len(product.images) >= MAX_IMAGES_PER_PRODUCT:
            raise ConflictError(f"A jar can have at most {MAX_IMAGES_PER_PRODUCT} photos. Remove one first.")
        filename = self.pipeline.store_file(file)
        try:
            product.images.append(ProductImage(filename=filename, alt_text=alt_text, position=len(product.images)))
            db.session.commit()
        except Exception:
            db.session.rollback()
            self.storage.delete(filename)
            raise
        activity_logger.info("product_image_added", f"product={product.id} file={filename}")
        return self.get(product.id)

    def make_main_image(self, image_id: int) -> Product:
        image = self._image(image_id)
        product = self.get(image.product_id)
        ordered = [image, *(other for other in product.images if other.id != image.id)]
        self._renumber(ordered)
        db.session.commit()
        activity_logger.info("product_image_main", f"product={product.id} image={image.id}")
        return self.get(product.id)

    def delete_image(self, image_id: int) -> Product:
        image = self._image(image_id)
        product = self.get(image.product_id)
        filename = image.filename
        product.images.remove(image)
        self._renumber(product.images)
        db.session.commit()
        self.storage.delete(filename)
        activity_logger.info("product_image_removed", f"product={product.id} file={filename}")
        return self.get(product.id)

    def _apply(self, product: Product, data: AdminProductRequest) -> None:
        with db.session.no_autoflush:
            name = self._required_text(data.name, "Give the jar a name.")
            slug = data.slug or slugify(name)
            if not slug:
                raise ValidationError("Choose a web address for this jar, using letters, numbers and dashes.")
            if self.products.slug_taken_by_other(slug, product.id):
                raise ConflictError(f"Another jar already uses the web address /products/{slug}.")
            category = self.categories.get_by_slug(data.category_slug)
            if category is None:
                raise ValidationError("Choose one of the shop's shelves.")
            product.name = name
            product.slug = slug
            product.category = category
            product.description = self._required_text(data.description, "Write a short description of the jar.")
            product.price_cents = data.price_cents
            product.weight_grams = data.weight_grams
            product.stock = data.stock
            product.is_active = data.is_active
            product.ingredients = [self.ingredients.get_or_create(name) for name in self._ingredient_names(data.ingredients)]

    def _image(self, image_id: int) -> ProductImage:
        image = self.images.get(image_id)
        if image is None:
            raise NotFoundError("We could not find this photo.")
        return image

    @staticmethod
    def _renumber(images: Sequence[ProductImage]) -> None:
        for position, image in enumerate(images):
            image.position = position

    @staticmethod
    def _ingredient_names(raw_names: list[str]) -> list[str]:
        names: list[str] = []
        for raw in raw_names:
            name = plain_text(raw).lower()
            if name and name not in names:
                names.append(name)
        return names

    @staticmethod
    def _required_text(value: str, message: str) -> str:
        cleaned = plain_text(value)
        if not cleaned:
            raise ValidationError(message)
        return cleaned

    @staticmethod
    def _snapshot(product: Product) -> dict:
        return {field: frozen_value(getattr(product, field)) for field in TRACKED_FIELDS}


def frozen_value(value):
    return list(value) if isinstance(value, list) else value
