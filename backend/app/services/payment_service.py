from app.errors import ConflictError, NotFoundError, OutOfStockError
from app.extensions import db
from app.models import Order, OrderStatusCode, Payment, PaymentStatus
from app.repositories import OrderRepository
from app.services.activity_logger import activity_logger
from app.services.payments import CheckoutSession, PaymentGateway, get_payment_gateway

NEW_ORDER_HINT = "Please cancel this order and place a new one."


class PaymentService:
    def __init__(self, gateway: PaymentGateway | None = None, orders: OrderRepository | None = None) -> None:
        self.gateway = gateway or get_payment_gateway()
        self.orders = orders or OrderRepository()

    def start(self, order_id: int, user_id: int) -> CheckoutSession:
        order = self._payable_order(order_id, user_id)
        self._close_open_checkout(order.payment)
        checkout = self.gateway.create_checkout(order)
        self._record_pending(order, checkout)
        db.session.commit()
        activity_logger.info(
            "payment_started", f"order={order.id} amount_cents={order.total_cents} reference={checkout.reference}"
        )
        return checkout

    def _payable_order(self, order_id: int, user_id: int) -> Order:
        order = self.orders.get_for_user(order_id, user_id)
        if order is None:
            raise NotFoundError("We could not find this order.")
        if order.status.code != OrderStatusCode.PENDING_PAYMENT.value:
            raise ConflictError("This order is not waiting for payment.")
        self._ensure_in_stock(order)
        return order

    @staticmethod
    def _ensure_in_stock(order: Order) -> None:
        for item in order.items:
            product = item.product
            if not product.is_active:
                raise OutOfStockError(f"{product.name} is no longer for sale. {NEW_ORDER_HINT}")
            if item.quantity > product.stock:
                raise OutOfStockError(f"Only {product.stock} left of {product.name}. {NEW_ORDER_HINT}")

    def _close_open_checkout(self, payment: Payment | None) -> None:
        if payment is None or payment.status != PaymentStatus.PENDING.value:
            return
        self.gateway.expire_checkout(payment.provider_reference)
        payment.status = PaymentStatus.FAILED.value
        db.session.commit()

    def _record_pending(self, order: Order, checkout: CheckoutSession) -> None:
        if order.payment is None:
            order.payment = Payment()
        payment = order.payment
        payment.provider = self.gateway.provider.value
        payment.provider_reference = checkout.reference
        payment.amount_cents = order.total_cents
        payment.status = PaymentStatus.PENDING.value
        payment.paid_at = None
