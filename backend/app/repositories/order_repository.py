from typing import Collection, Sequence

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models import PURCHASED_STATUSES, Order, OrderItem, OrderStatus, Payment
from app.repositories.base import SqlAlchemyRepository


class OrderRepository(SqlAlchemyRepository[Order]):
    model = Order

    def list_for_user(self, user_id: int) -> Sequence[Order]:
        statement = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product), selectinload(Order.status))
            .order_by(Order.created_at.desc(), Order.id.desc())
        )
        return self.session.scalars(statement).all()

    def get_for_user(self, order_id: int, user_id: int) -> Order | None:
        return self.find_one_by(id=order_id, user_id=user_id)

    def list_by_status(self, status_code: str | None = None) -> Sequence[Order]:
        statement = select(Order).join(Order.status).order_by(Order.created_at.desc(), Order.id.desc())
        if status_code:
            statement = statement.where(OrderStatus.code == status_code)
        return self.session.scalars(statement).all()

    def user_has_purchased(self, user_id: int, product_id: int) -> bool:
        statement = (
            select(OrderItem.order_id)
            .join(OrderItem.order)
            .join(Order.status)
            .where(
                Order.user_id == user_id,
                OrderItem.product_id == product_id,
                OrderStatus.code.in_([status.value for status in PURCHASED_STATUSES]),
            )
            .limit(1)
        )
        return self.session.scalar(statement) is not None


class PaymentRepository(SqlAlchemyRepository[Payment]):
    model = Payment

    def get_by_provider_reference(self, reference: str) -> Payment | None:
        return self.find_one_by(provider_reference=reference)

    def change_status(self, payment_id: int, allowed: Collection[str], new_status: str) -> bool:
        statement = (
            update(Payment)
            .where(Payment.id == payment_id, Payment.status.in_(list(allowed)))
            .values(status=new_status)
        )
        return self.session.execute(statement).rowcount == 1
