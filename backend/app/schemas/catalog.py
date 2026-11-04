from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models import Product, ProductImage, Review
from app.repositories.product_repository import ProductPage, ProductSort

SearchText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
Slug = Annotated[str, StringConstraints(strip_whitespace=True, max_length=80)]


class ProductQuery(BaseModel):
    q: SearchText | None = None
    category: Slug | None = None
    sort: ProductSort = ProductSort.NEWEST
    page: int = Field(default=1, ge=1, le=1000)
    per_page: int = Field(default=12, ge=1, le=48)


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str


class CategoryRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str


class ImageResponse(BaseModel):
    url: str
    alt_text: str

    @classmethod
    def from_image(cls, image: ProductImage) -> "ImageResponse":
        return cls(url=f"/uploads/{image.filename}", alt_text=image.alt_text)


class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str
    author: str
    created_at: datetime

    @classmethod
    def from_review(cls, review: Review) -> "ReviewResponse":
        return cls(
            id=review.id,
            rating=review.rating,
            comment=review.comment,
            author=f"{review.user.first_name} {review.user.last_name[:1]}.",
            created_at=review.created_at,
        )


class ProductSummary(BaseModel):
    id: int
    name: str
    slug: str
    price_cents: int
    weight_grams: int
    stock: int
    category: CategoryRef
    image: ImageResponse | None

    @classmethod
    def summary_fields(cls, product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "price_cents": product.price_cents,
            "weight_grams": product.weight_grams,
            "stock": product.stock,
            "category": CategoryRef.model_validate(product.category),
            "image": ImageResponse.from_image(product.images[0]) if product.images else None,
        }

    @classmethod
    def from_product(cls, product: Product) -> "ProductSummary":
        return cls(**cls.summary_fields(product))


class ProductDetail(ProductSummary):
    description: str
    images: list[ImageResponse]
    ingredients: list[str]
    average_rating: float | None
    reviews: list[ReviewResponse]

    @classmethod
    def from_product(cls, product: Product) -> "ProductDetail":
        newest_first = sorted(product.reviews, key=lambda review: review.created_at, reverse=True)
        return cls(
            **cls.summary_fields(product),
            description=product.description,
            images=[ImageResponse.from_image(image) for image in product.images],
            ingredients=[ingredient.name for ingredient in product.ingredients],
            average_rating=product.average_rating,
            reviews=[ReviewResponse.from_review(review) for review in newest_first],
        )


class ProductPageResponse(BaseModel):
    items: list[ProductSummary]
    total: int
    page: int
    per_page: int
    pages: int

    @classmethod
    def from_page(cls, page: ProductPage) -> "ProductPageResponse":
        return cls(
            items=[ProductSummary.from_product(product) for product in page.items],
            total=page.total,
            page=page.page,
            per_page=page.per_page,
            pages=page.pages,
        )

