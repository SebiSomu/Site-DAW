from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models import CartLine, CartSummary, Order, OrderItem
from app.schemas.auth import RequestSchema
from app.schemas.catalog import ProductSummary

Street = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
City = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
County = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
PostalCode = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[0-9]{6}$")]

MAX_CART_LINES = 50
MAX_JARS_PER_LINE = 99


class CartItemRequest(RequestSchema):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=MAX_JARS_PER_LINE)


class CartRequest(RequestSchema):
    items: list[CartItemRequest] = Field(max_length=MAX_CART_LINES)


class AddressRequest(RequestSchema):
    street: Street
    city: City
    county: County
    postal_code: PostalCode


class OrderRequest(RequestSchema):
    address_id: int = Field(gt=0)
    items: list[CartItemRequest] = Field(min_length=1, max_length=MAX_CART_LINES)
    notes: str = Field(default="", max_length=500)


class ReviewRequest(RequestSchema):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=2000)


class CartLineResponse(BaseModel):
    product: ProductSummary
    quantity: int
    subtotal_cents: int
    is_available: bool

    @classmethod
    def from_line(cls, line: CartLine) -> "CartLineResponse":
        return cls(
            product=ProductSummary.from_product(line.product),
            quantity=line.quantity,
            subtotal_cents=line.subtotal_cents,
            is_available=line.is_available,
        )


class CartResponse(BaseModel):
    lines: list[CartLineResponse]
    missing_product_ids: list[int]
    total_cents: int

    @classmethod
    def from_summary(cls, summary: CartSummary) -> "CartResponse":
        return cls(
            lines=[CartLineResponse.from_line(line) for line in summary.lines],
            missing_product_ids=summary.missing_product_ids,
            total_cents=summary.total_cents,
        )


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    street: str
    city: str
    county: str
    postal_code: str
    one_line: str


class OrderStatusRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str


class OrderItemResponse(BaseModel):
    product_name: str
    product_slug: str
    quantity: int
    unit_price_cents: int
    subtotal_cents: int

    @classmethod
    def from_item(cls, item: OrderItem) -> "OrderItemResponse":
        return cls(
            product_name=item.product.name,
            product_slug=item.product.slug,
            quantity=item.quantity,
            unit_price_cents=item.unit_price_cents,
            subtotal_cents=item.subtotal_cents,
        )


class OrderSummary(BaseModel):
    id: int
    status: OrderStatusRef
    created_at: datetime
    total_cents: int
    jar_count: int
    is_cancellable: bool

    @classmethod
    def summary_fields(cls, order: Order) -> dict:
        return {
            "id": order.id,
            "status": OrderStatusRef.model_validate(order.status),
            "created_at": order.created_at,
            "total_cents": order.total_cents,
            "jar_count": sum(item.quantity for item in order.items),
            "is_cancellable": order.is_cancellable,
        }

    @classmethod
    def from_order(cls, order: Order) -> "OrderSummary":
        return cls(**cls.summary_fields(order))


class OrderDetail(OrderSummary):
    items: list[OrderItemResponse]
    ships_to: str
    notes: str

    @classmethod
    def from_order(cls, order: Order) -> "OrderDetail":
        return cls(
            **cls.summary_fields(order),
            items=[OrderItemResponse.from_item(item) for item in order.items],
            ships_to=order.address.one_line,
            notes=order.notes,
        )
