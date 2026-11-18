from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.models import Order, OrderStatus, OrderStatusCode, Product, ProductImage, User
from app.schemas.auth import RequestSchema
from app.schemas.catalog import CategoryRef
from app.schemas.shop import OrderItemResponse, OrderStatusRef

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


class AdminOrderQuery(RequestSchema):
    status: OrderStatusCode | None = None


class OrderStatusChangeRequest(RequestSchema):
    status: OrderStatusCode


class CustomerRef(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None

    @classmethod
    def from_user(cls, user: User) -> "CustomerRef":
        return cls(id=user.id, name=f"{user.first_name} {user.last_name}", email=user.email, phone=user.phone)


class AdminOrderSummary(BaseModel):
    id: int
    status: OrderStatusRef
    created_at: datetime
    total_cents: int
    jar_count: int
    customer: CustomerRef
    payment_status: str | None

    @classmethod
    def summary_fields(cls, order: Order) -> dict:
        return {
            "id": order.id,
            "status": OrderStatusRef.model_validate(order.status),
            "created_at": order.created_at,
            "total_cents": order.total_cents,
            "jar_count": sum(item.quantity for item in order.items),
            "customer": CustomerRef.from_user(order.user),
            "payment_status": order.payment.status if order.payment else None,
        }

    @classmethod
    def from_order(cls, order: Order) -> "AdminOrderSummary":
        return cls(**cls.summary_fields(order))


class AdminOrderDetail(AdminOrderSummary):
    items: list[OrderItemResponse]
    ships_to: str
    notes: str
    paid_at: datetime | None
    next_statuses: list[OrderStatusRef]

    @classmethod
    def from_order(cls, order: Order, next_statuses: list[OrderStatus]) -> "AdminOrderDetail":
        return cls(
            **cls.summary_fields(order),
            items=[OrderItemResponse.from_item(item) for item in order.items],
            ships_to=order.address.one_line,
            notes=order.notes,
            paid_at=order.payment.paid_at if order.payment else None,
            next_statuses=[OrderStatusRef.model_validate(status) for status in next_statuses],
        )


class StatusCount(BaseModel):
    code: str
    name: str
    count: int


class LowStockJar(BaseModel):
    id: int
    name: str
    slug: str
    stock: int
    is_active: bool

    @classmethod
    def from_product(cls, product: Product) -> "LowStockJar":
        return cls(id=product.id, name=product.name, slug=product.slug, stock=product.stock, is_active=product.is_active)


class AdminSummaryResponse(BaseModel):
    revenue_cents: int
    paid_orders: int
    orders_to_send: int
    awaiting_payment: int
    messages: int
    orders_by_status: list[StatusCount]
    low_stock: list[LowStockJar]
    recent_orders: list[AdminOrderSummary]
