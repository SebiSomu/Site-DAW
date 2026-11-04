from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.enums import CANCELLABLE_STATUSES, OrderStatusCode
from app.models.mixins import IdMixin, TimestampMixin


class OrderStatus(IdMixin, db.Model):
    __tablename__ = "order_statuses"

    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    orders: Mapped[list["Order"]] = relationship(back_populates="status")


class Order(IdMixin, TimestampMixin, db.Model):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id", ondelete="RESTRICT"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("order_statuses.id", ondelete="RESTRICT"), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    user: Mapped["User"] = relationship(back_populates="orders")
    address: Mapped["Address"] = relationship(back_populates="orders")
    status: Mapped[OrderStatus] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payment: Mapped["Payment | None"] = relationship(back_populates="order", uselist=False, cascade="all, delete-orphan")

    @property
    def total_cents(self) -> int:
        return sum(item.subtotal_cents for item in self.items)

    @property
    def is_cancellable(self) -> bool:
        return OrderStatusCode(self.status.code) in CANCELLABLE_STATUSES


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price_cents > 0", name="unit_price_positive"),
    )

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")

    @property
    def subtotal_cents(self) -> int:
        return self.quantity * self.unit_price_cents


class Payment(IdMixin, db.Model):
    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount_cents > 0", name="amount_positive"),)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_reference: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    order: Mapped[Order] = relationship(back_populates="payment")
