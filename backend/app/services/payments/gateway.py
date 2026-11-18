from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from app.models import Order, PaymentProvider


class CheckoutStatus(str, Enum):
    OPEN = "open"
    COMPLETE = "complete"
    EXPIRED = "expired"


class PaymentEventKind(str, Enum):
    COMPLETED = "completed"
    EXPIRED = "expired"
    IGNORED = "ignored"


@dataclass(frozen=True)
class CheckoutSession:
    reference: str
    url: str


@dataclass(frozen=True)
class PaymentEvent:
    kind: PaymentEventKind
    reference: str | None = None
    amount_cents: int | None = None
    is_paid: bool = False


class PaymentGateway(ABC):
    provider: PaymentProvider

    @abstractmethod
    def create_checkout(self, order: Order) -> CheckoutSession: ...

    @abstractmethod
    def parse_webhook(self, payload: bytes, signature: str | None) -> PaymentEvent: ...

    @abstractmethod
    def expire_checkout(self, reference: str) -> None: ...

    @abstractmethod
    def refund(self, reference: str) -> None: ...
