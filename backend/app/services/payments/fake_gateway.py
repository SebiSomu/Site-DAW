import json
from dataclasses import dataclass
from uuid import uuid4

from app.errors import CheckoutAlreadyPaidError, PaymentError, WebhookError
from app.models import Order, PaymentProvider
from app.services.payments.gateway import (
    CheckoutSession,
    CheckoutStatus,
    PaymentEvent,
    PaymentEventKind,
    PaymentGateway,
)

FAKE_SIGNATURE = "fake-signature"


@dataclass
class FakeCheckout:
    order_id: int
    amount_cents: int
    status: CheckoutStatus = CheckoutStatus.OPEN


class FakeGateway(PaymentGateway):
    provider = PaymentProvider.FAKE

    def __init__(self, site_url: str) -> None:
        self.site_url = site_url.rstrip("/")
        self.checkouts: dict[str, FakeCheckout] = {}
        self.refunded: list[str] = []
        self.is_down = False

    def create_checkout(self, order: Order) -> CheckoutSession:
        self._ensure_up()
        reference = f"fake_session_{uuid4().hex}"
        self.checkouts[reference] = FakeCheckout(order.id, order.total_cents)
        return CheckoutSession(reference=reference, url=f"{self.site_url}/checkout/success?order={order.id}")

    def parse_webhook(self, payload: bytes, signature: str | None) -> PaymentEvent:
        if signature != FAKE_SIGNATURE:
            raise WebhookError()
        try:
            body = json.loads(payload)
            return PaymentEvent(
                kind=PaymentEventKind(body["kind"]),
                reference=body.get("reference"),
                amount_cents=body.get("amount_cents"),
                is_paid=body.get("is_paid", False),
            )
        except (ValueError, KeyError, TypeError) as error:
            raise WebhookError() from error

    def expire_checkout(self, reference: str) -> None:
        self._ensure_up()
        checkout = self._get(reference)
        if checkout.status is CheckoutStatus.COMPLETE:
            raise CheckoutAlreadyPaidError()
        checkout.status = CheckoutStatus.EXPIRED

    def refund(self, reference: str) -> None:
        self._ensure_up()
        if self._get(reference).status is not CheckoutStatus.COMPLETE:
            raise PaymentError("There is no payment to refund for this order.")
        if reference not in self.refunded:
            self.refunded.append(reference)

    def complete(self, reference: str) -> bytes:
        checkout = self._get(reference)
        checkout.status = CheckoutStatus.COMPLETE
        return self.event_payload(PaymentEventKind.COMPLETED, reference, checkout.amount_cents, is_paid=True)

    def expire_event(self, reference: str) -> bytes:
        checkout = self._get(reference)
        checkout.status = CheckoutStatus.EXPIRED
        return self.event_payload(PaymentEventKind.EXPIRED, reference, checkout.amount_cents)

    @staticmethod
    def event_payload(
        kind: PaymentEventKind, reference: str | None = None, amount_cents: int | None = None, is_paid: bool = False
    ) -> bytes:
        return json.dumps(
            {"kind": kind.value, "reference": reference, "amount_cents": amount_cents, "is_paid": is_paid}
        ).encode()

    def _get(self, reference: str) -> FakeCheckout:
        checkout = self.checkouts.get(reference)
        if checkout is None:
            raise PaymentError()
        return checkout

    def _ensure_up(self) -> None:
        if self.is_down:
            raise PaymentError()
