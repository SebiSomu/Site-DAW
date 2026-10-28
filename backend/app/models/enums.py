from enum import Enum


class RoleName(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"


class OrderStatusCode(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


ORDER_STATUS_LABELS: dict[OrderStatusCode, str] = {
    OrderStatusCode.PENDING_PAYMENT: "În așteptarea plății",
    OrderStatusCode.PAID: "Plătită",
    OrderStatusCode.CONFIRMED: "Confirmată",
    OrderStatusCode.SHIPPED: "Expediată",
    OrderStatusCode.DELIVERED: "Livrată",
    OrderStatusCode.CANCELLED: "Anulată",
}

CANCELLABLE_STATUSES = frozenset(
    {OrderStatusCode.PENDING_PAYMENT, OrderStatusCode.PAID, OrderStatusCode.CONFIRMED}
)


PURCHASED_STATUSES = frozenset(
    {OrderStatusCode.PAID, OrderStatusCode.CONFIRMED, OrderStatusCode.SHIPPED, OrderStatusCode.DELIVERED}
)


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentProvider(str, Enum):
    STRIPE = "stripe"
