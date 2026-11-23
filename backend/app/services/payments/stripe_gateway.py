import time
from functools import wraps

import stripe

from app.errors import CheckoutAlreadyPaidError, PaymentError, WebhookError
from app.models import Order, PaymentProvider
from app.services.activity_logger import activity_logger
from app.services.payments.gateway import (
    CheckoutSession,
    CheckoutStatus,
    PaymentEvent,
    PaymentEventKind,
    PaymentGateway,
)

CURRENCY = "ron"
CHECKOUT_LIFETIME_SECONDS = 60 * 60
NOT_SET_UP = "Card payments are not set up yet."
EVENT_KINDS = {
    "checkout.session.completed": PaymentEventKind.COMPLETED,
    "checkout.session.expired": PaymentEventKind.EXPIRED,
}


def describe_stripe_error(error: stripe.StripeError) -> str:
    return f"{type(error).__name__} code={error.code or '-'} param={getattr(error, 'param', None) or '-'}"


def reports_gateway_errors(method):
    @wraps(method)
    def guarded(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except stripe.StripeError as error:
            activity_logger.warning("payment_gateway_error", describe_stripe_error(error))
            raise PaymentError() from error

    return guarded


class StripeGateway(PaymentGateway):
    provider = PaymentProvider.STRIPE

    def __init__(
        self,
        secret_key: str,
        webhook_secret: str,
        site_url: str,
        http_client: stripe.HTTPClient | None = None,
    ) -> None:
        self.webhook_secret = webhook_secret
        self.site_url = site_url.rstrip("/")
        self.client = stripe.StripeClient(secret_key, http_client=http_client) if secret_key else None

    @reports_gateway_errors
    def create_checkout(self, order: Order) -> CheckoutSession:
        session = self._stripe().v1.checkout.sessions.create(params=self._checkout_params(order))
        return CheckoutSession(reference=session.id, url=session.url)

    def parse_webhook(self, payload: bytes, signature: str | None) -> PaymentEvent:
        if not self.webhook_secret:
            raise PaymentError(NOT_SET_UP)
        try:
            event = stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
        except (ValueError, stripe.SignatureVerificationError) as error:
            raise WebhookError() from error
        kind = EVENT_KINDS.get(event.type)
        if kind is None:
            return PaymentEvent(kind=PaymentEventKind.IGNORED)
        session = event.data.object
        return PaymentEvent(
            kind=kind,
            reference=session.id,
            amount_cents=session.amount_total,
            is_paid=session.payment_status == "paid",
        )

    @reports_gateway_errors
    def expire_checkout(self, reference: str) -> None:
        sessions = self._stripe().v1.checkout.sessions
        status = sessions.retrieve(reference).status
        if status == CheckoutStatus.COMPLETE.value:
            raise CheckoutAlreadyPaidError()
        if status == CheckoutStatus.OPEN.value:
            sessions.expire(reference)

    @reports_gateway_errors
    def refund(self, reference: str) -> None:
        client = self._stripe()
        payment_intent = client.v1.checkout.sessions.retrieve(reference).payment_intent
        if not payment_intent:
            raise PaymentError("There is no payment to refund for this order.")
        client.v1.refunds.create(
            params={"payment_intent": payment_intent},
            options={"idempotency_key": f"refund-{reference}"},
        )

    def _stripe(self) -> stripe.StripeClient:
        if self.client is None:
            raise PaymentError(NOT_SET_UP)
        return self.client

    def _checkout_params(self, order: Order) -> dict:
        return {
            "mode": "payment",
            "client_reference_id": str(order.id),
            "metadata": {"order_id": str(order.id)},
            "expires_at": int(time.time()) + CHECKOUT_LIFETIME_SECONDS,
            "success_url": f"{self.site_url}/checkout/success?order={order.id}",
            "cancel_url": f"{self.site_url}/checkout/cancelled?order={order.id}",
            "line_items": [
                {
                    "quantity": item.quantity,
                    "price_data": {
                        "currency": CURRENCY,
                        "unit_amount": item.unit_price_cents,
                        "product_data": {"name": item.product.name},
                    },
                }
                for item in order.items
            ],
        }
