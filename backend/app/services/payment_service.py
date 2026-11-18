from datetime import datetime, timezone

from app.errors import ConflictError, NotFoundError, OutOfStockError, WebhookError
from app.extensions import db
from app.models import Order, OrderStatusCode, Payment, PaymentStatus
from app.repositories import OrderRepository, OrderStatusRepository, PaymentRepository, ProductRepository
from app.services.activity_logger import activity_logger
from app.services.payments import CheckoutSession, PaymentEvent, PaymentEventKind, PaymentGateway, get_payment_gateway

NEW_ORDER_HINT = "Please cancel this order and place a new one."
SETTLED_PAYMENTS = frozenset({PaymentStatus.SUCCEEDED.value, PaymentStatus.REFUNDED.value})


class PaymentService:
    def __init__(
        self,
        gateway: PaymentGateway | None = None,
        orders: OrderRepository | None = None,
        payments: PaymentRepository | None = None,
        products: ProductRepository | None = None,
        statuses: OrderStatusRepository | None = None,
    ) -> None:
        self.gateway = gateway or get_payment_gateway()
        self.orders = orders or OrderRepository()
        self.payments = payments or PaymentRepository()
        self.products = products or ProductRepository()
        self.statuses = statuses or OrderStatusRepository()

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

    def handle_webhook(self, payload: bytes, signature: str | None) -> None:
        event = self._verified_event(payload, signature)
        if event.kind is PaymentEventKind.COMPLETED:
            self._on_completed(event)
        elif event.kind is PaymentEventKind.EXPIRED:
            self._on_expired(event)

    def _payable_order(self, order_id: int, user_id: int) -> Order:
        order = self.orders.get_for_user(order_id, user_id)
        if order is None:
            raise NotFoundError("We could not find this order.")
        if not self._has_status(order, OrderStatusCode.PENDING_PAYMENT):
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

    def _verified_event(self, payload: bytes, signature: str | None) -> PaymentEvent:
        try:
            return self.gateway.parse_webhook(payload, signature)
        except WebhookError:
            activity_logger.warning("webhook_rejected", f"bytes={len(payload)} signed={signature is not None}")
            raise

    def _known_payment(self, event: PaymentEvent) -> Payment | None:
        payment = self.payments.get_by_provider_reference(event.reference) if event.reference else None
        if payment is None:
            activity_logger.warning("webhook_unknown_session", f"reference={event.reference}")
        return payment

    def _on_completed(self, event: PaymentEvent) -> None:
        payment = self._known_payment(event)
        if payment is None or not event.is_paid or payment.status in SETTLED_PAYMENTS:
            return
        order = payment.order
        if self._has_status(order, OrderStatusCode.CANCELLED):
            self._refund(payment, "order already cancelled")
        elif event.amount_cents != payment.amount_cents:
            self._refund(payment, f"amount mismatch expected={payment.amount_cents} received={event.amount_cents}")
        elif not self._has_status(order, OrderStatusCode.PENDING_PAYMENT):
            activity_logger.warning("webhook_ignored", f"order={order.id} status={order.status.code}")
        elif self._take_stock(order):
            self._mark_paid(payment)
        else:
            db.session.rollback()
            self._refund(payment, "a jar sold out before the payment arrived")

    def _on_expired(self, event: PaymentEvent) -> None:
        payment = self._known_payment(event)
        if payment is None or payment.status != PaymentStatus.PENDING.value:
            return
        payment.status = PaymentStatus.FAILED.value
        db.session.commit()
        activity_logger.info("payment_failed", f"order={payment.order_id} reason=checkout expired")

    def _take_stock(self, order: Order) -> bool:
        return all(self.products.take_stock(item.product_id, item.quantity) for item in order.items)

    def _mark_paid(self, payment: Payment) -> None:
        payment.status = PaymentStatus.SUCCEEDED.value
        payment.paid_at = datetime.now(timezone.utc)
        payment.order.status = self.statuses.get_by_code(OrderStatusCode.PAID)
        db.session.commit()
        activity_logger.info("payment_succeeded", f"order={payment.order_id} amount_cents={payment.amount_cents}")

    def _refund(self, payment: Payment, reason: str) -> None:
        self.gateway.refund(payment.provider_reference)
        payment.status = PaymentStatus.REFUNDED.value
        payment.order.status = self.statuses.get_by_code(OrderStatusCode.CANCELLED)
        db.session.commit()
        activity_logger.warning("payment_refunded", f"order={payment.order_id} reason={reason}")

    @staticmethod
    def _has_status(order: Order, code: OrderStatusCode) -> bool:
        return order.status.code == code.value
