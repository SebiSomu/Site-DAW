from typing import Sequence

from app.errors import ConflictError, NotFoundError, OutOfStockError
from app.extensions import db
from app.models import CartSummary, Order, OrderItem, OrderStatusCode
from app.repositories import OrderRepository, OrderStatusRepository
from app.schemas import OrderRequest
from app.security.sanitize import plain_text
from app.services.activity_logger import activity_logger
from app.services.address_service import AddressService
from app.services.cart_service import CartService
from app.services.payment_service import PaymentService


class OrderService:
    def __init__(
        self,
        orders: OrderRepository | None = None,
        statuses: OrderStatusRepository | None = None,
        addresses: AddressService | None = None,
        cart: CartService | None = None,
        payments: PaymentService | None = None,
    ) -> None:
        self.orders = orders or OrderRepository()
        self.statuses = statuses or OrderStatusRepository()
        self.addresses = addresses or AddressService()
        self.cart = cart or CartService()
        self.payments = payments or PaymentService()

    def place(self, user_id: int, data: OrderRequest) -> Order:
        address = self.addresses.get_active(data.address_id, user_id)
        summary = self.cart.price(data.items)
        self._ensure_available(summary)
        order = Order(
            user_id=user_id,
            address=address,
            status=self.statuses.get_by_code(OrderStatusCode.PENDING_PAYMENT),
            notes=plain_text(data.notes),
            items=[
                OrderItem(product=line.product, quantity=line.quantity, unit_price_cents=line.product.price_cents)
                for line in summary.lines
            ],
        )
        self.orders.add(order)
        db.session.commit()
        activity_logger.info("order_created", f"order={order.id} total_cents={order.total_cents}")
        return order

    def list_for_user(self, user_id: int) -> Sequence[Order]:
        return self.orders.list_for_user(user_id)

    def get_for_user(self, order_id: int, user_id: int) -> Order:
        order = self.orders.get_for_user(order_id, user_id)
        if order is None:
            raise NotFoundError("We could not find this order.")
        return order

    def cancel(self, order_id: int, user_id: int) -> Order:
        order = self.get_for_user(order_id, user_id)
        if not order.is_cancellable:
            raise ConflictError("This order can no longer be cancelled.")
        self.payments.release_for_cancellation(order)
        order.status = self.statuses.get_by_code(OrderStatusCode.CANCELLED)
        db.session.commit()
        activity_logger.info("order_cancelled", f"order={order.id}")
        return order

    @staticmethod
    def _ensure_available(summary: CartSummary) -> None:
        if summary.missing_product_ids:
            raise OutOfStockError("One of the jars in your cart is no longer for sale.")
        for line in summary.lines:
            if not line.is_available:
                raise OutOfStockError(f"Only {line.product.stock} left of {line.product.name}. Please change your cart.")
