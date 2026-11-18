from typing import Sequence

from app.errors import ConflictError, NotFoundError
from app.extensions import db
from app.models import ORDER_STATUS_LABELS, Order, OrderStatus, OrderStatusCode, PURCHASED_STATUSES
from app.repositories import ContactMessageRepository, OrderRepository, OrderStatusRepository, ProductRepository
from app.schemas import AdminOrderSummary, AdminSummaryResponse, LowStockJar, StatusCount
from app.services.activity_logger import activity_logger
from app.services.payment_service import PaymentService

ADMIN_TRANSITIONS: dict[OrderStatusCode, tuple[OrderStatusCode, ...]] = {
    OrderStatusCode.PENDING_PAYMENT: (OrderStatusCode.CANCELLED,),
    OrderStatusCode.PAID: (OrderStatusCode.CONFIRMED, OrderStatusCode.CANCELLED),
    OrderStatusCode.CONFIRMED: (OrderStatusCode.SHIPPED, OrderStatusCode.CANCELLED),
    OrderStatusCode.SHIPPED: (OrderStatusCode.DELIVERED,),
}
TO_SEND = (OrderStatusCode.PAID, OrderStatusCode.CONFIRMED)
LOW_STOCK_THRESHOLD = 5
RECENT_ORDERS = 5


class AdminOrderService:
    def __init__(
        self,
        orders: OrderRepository | None = None,
        statuses: OrderStatusRepository | None = None,
        products: ProductRepository | None = None,
        messages: ContactMessageRepository | None = None,
        payments: PaymentService | None = None,
    ) -> None:
        self.orders = orders or OrderRepository()
        self.statuses = statuses or OrderStatusRepository()
        self.products = products or ProductRepository()
        self.messages = messages or ContactMessageRepository()
        self._payments = payments

    @property
    def payments(self) -> PaymentService:
        self._payments = self._payments or PaymentService()
        return self._payments

    def list_orders(self, status: OrderStatusCode | None = None) -> Sequence[Order]:
        return self.orders.list_for_admin(status.value if status else None)

    def get(self, order_id: int) -> Order:
        order = self.orders.get_for_admin(order_id)
        if order is None:
            raise NotFoundError("We could not find this order.")
        return order

    def next_statuses(self, order: Order) -> list[OrderStatus]:
        return [self.statuses.get_by_code(code) for code in ADMIN_TRANSITIONS.get(OrderStatusCode(order.status.code), ())]

    def change_status(self, order_id: int, target: OrderStatusCode) -> Order:
        order = self.get(order_id)
        current = OrderStatusCode(order.status.code)
        if target not in ADMIN_TRANSITIONS.get(current, ()):
            raise ConflictError(
                f"An order that is {ORDER_STATUS_LABELS[current]} cannot be marked {ORDER_STATUS_LABELS[target]}."
            )
        if target is OrderStatusCode.CANCELLED:
            self._cancel(order)
        else:
            self._advance(order, current, target)
        activity_logger.info(
            "order_status_changed", f"order={order.id} from={current.value} to={target.value} by=admin"
        )
        db.session.expire_all()
        return self.get(order_id)

    def summary(self) -> AdminSummaryResponse:
        counts = self.orders.count_by_status()
        statuses = sorted(self.statuses.list_all(), key=lambda status: list(OrderStatusCode).index(OrderStatusCode(status.code)))
        return AdminSummaryResponse(
            revenue_cents=self.orders.revenue_cents(),
            paid_orders=sum(counts.get(code.value, 0) for code in PURCHASED_STATUSES),
            orders_to_send=sum(counts.get(code.value, 0) for code in TO_SEND),
            awaiting_payment=counts.get(OrderStatusCode.PENDING_PAYMENT.value, 0),
            messages=self.messages.count(),
            orders_by_status=[
                StatusCount(code=status.code, name=status.name, count=counts.get(status.code, 0)) for status in statuses
            ],
            low_stock=[LowStockJar.from_product(product) for product in self.products.list_low_stock(LOW_STOCK_THRESHOLD)],
            recent_orders=[
                AdminOrderSummary.from_order(order) for order in self.orders.list_for_admin(limit=RECENT_ORDERS)
            ],
        )

    def _cancel(self, order: Order) -> None:
        self.payments.release_for_cancellation(order)
        order.status = self.statuses.get_by_code(OrderStatusCode.CANCELLED)
        db.session.commit()
        activity_logger.info("order_cancelled", f"order={order.id} by=admin")

    def _advance(self, order: Order, current: OrderStatusCode, target: OrderStatusCode) -> None:
        moved = self.orders.change_status(
            order.id, self.statuses.get_by_code(current).id, self.statuses.get_by_code(target).id
        )
        if not moved:
            db.session.rollback()
            raise ConflictError("This order changed a moment ago. Refresh the page and try again.")
        db.session.commit()
