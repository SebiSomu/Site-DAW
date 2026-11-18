from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.models import Product, ProductImage
from app.schemas.auth import RequestSchema
from app.schemas.catalog import CategoryRef

ProductName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
ProductSlug = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=140, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
]
CategorySlug = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
IngredientName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
AltText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]

MAX_PRICE_CENTS = 1_000_000
MAX_WEIGHT_GRAMS = 10_000
MAX_STOCK = 10_000
MAX_INGREDIENTS = 20


class AdminProductRequest(RequestSchema):
    name: ProductName
    slug: ProductSlug | None = None
    category_slug: CategorySlug
    description: str = Field(min_length=1, max_length=4000)
    price_cents: int = Field(ge=1, le=MAX_PRICE_CENTS)
    weight_grams: int = Field(ge=1, le=MAX_WEIGHT_GRAMS)
    stock: int = Field(ge=0, le=MAX_STOCK)
    ingredients: list[IngredientName] = Field(default_factory=list, max_length=MAX_INGREDIENTS)
    is_active: bool = True


class ImageUploadForm(RequestSchema):
    alt_text: AltText


class AdminImageResponse(BaseModel):
    id: int
    url: str
    alt_text: str
    position: int

    @classmethod
    def from_image(cls, image: ProductImage) -> "AdminImageResponse":
        return cls(id=image.id, url=f"/uploads/{image.filename}", alt_text=image.alt_text, position=image.position)


class AdminProductSummary(BaseModel):
    id: int
    name: str
    slug: str
    category: CategoryRef
    price_cents: int
    weight_grams: int
    stock: int
    is_active: bool
    image: AdminImageResponse | None
    image_count: int

    @classmethod
    def summary_fields(cls, product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "category": CategoryRef.model_validate(product.category),
            "price_cents": product.price_cents,
            "weight_grams": product.weight_grams,
            "stock": product.stock,
            "is_active": product.is_active,
            "image": AdminImageResponse.from_image(product.images[0]) if product.images else None,
            "image_count": len(product.images),
        }

    @classmethod
    def from_product(cls, product: Product) -> "AdminProductSummary":
        return cls(**cls.summary_fields(product))


class AdminProductDetail(AdminProductSummary):
    description: str
    ingredients: list[str]
    images: list[AdminImageResponse]
    created_at: datetime
    can_delete: bool

    @classmethod
    def from_product(cls, product: Product) -> "AdminProductDetail":
        return cls(
            **cls.summary_fields(product),
            description=product.description,
            ingredients=[ingredient.name for ingredient in product.ingredients],
            images=[AdminImageResponse.from_image(image) for image in product.images],
            created_at=product.created_at,
            can_delete=not product.order_items,
        )
