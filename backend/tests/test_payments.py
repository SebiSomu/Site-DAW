import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs

import pytest
import stripe

from app import create_app
from app.errors import CheckoutAlreadyPaidError, PaymentError, WebhookError
from app.models import Address, Order, OrderItem, OrderStatusCode
from app.repositories import AddressRepository, OrderRepository, OrderStatusRepository, ProductRepository, UserRepository
from app.seed import DEMO_CLIENT_EMAIL
from app.services.payments import (
    FAKE_SIGNATURE,
    CheckoutStatus,
    FakeGateway,
    PaymentEventKind,
    PaymentGateway,
    StripeGateway,
    build_gateway,
    get_payment_gateway,
)

WEBHOOK_SECRET = "whsec_test_secret"
SITE_URL = "https://shop.example"
PRODUCTION_SETTINGS = {
    "STRIPE_SECRET_KEY": "sk_test_key",
    "STRIPE_WEBHOOK_SECRET": WEBHOOK_SECRET,
    "SITE_URL": SITE_URL,
    "TURNSTILE_SITE_KEY": "site-key",
    "TURNSTILE_SECRET_KEY": "secret-key",
}
SESSION_URL = "https://checkout.stripe.com/c/pay/cs_test_1"


class RecordingHttpClient(stripe.HTTPClient):
    name = "recording"

    def __init__(self, *responses) -> None:
        super().__init__()
        self.responses = list(responses)
        self.requests = []

    def request(self, method, url, headers, post_data=None, *, _usage=None):
        self.requests.append({"method": method, "url": url, "headers": headers, "body": post_data})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        status, body = response
        return json.dumps(body), status, {}

    def close(self):
        return None


def session_body(status="open", payment_intent=None):
    return (
        200,
        {"id": "cs_test_1", "object": "checkout.session", "url": SESSION_URL, "status": status, "payment_intent": payment_intent},
    )


def stripe_gateway(*responses):
    http = RecordingHttpClient(*responses)
    return StripeGateway("sk_test_key", WEBHOOK_SECRET, f"{SITE_URL}/", http_client=http), http


def signed(payload: bytes, secret: str = WEBHOOK_SECRET, timestamp: int | None = None) -> str:
    moment = timestamp if timestamp is not None else int(time.time())
    digest = hmac.new(secret.encode(), f"{moment}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={moment},v1={digest}"


def stripe_event(event_type: str, **session_fields) -> bytes:
    session = {"id": "cs_test_1", "object": "checkout.session", "amount_total": 5200, "payment_status": "paid", **session_fields}
    return json.dumps({"id": "evt_1", "object": "event", "type": event_type, "data": {"object": session}}).encode()


def production_app(tmp_path, **settings):
    overrides = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "ACTIVITY_LOG_PATH": str(tmp_path / "activity.log"),
        **PRODUCTION_SETTINGS,
        **settings,
    }
    return create_app("production", overrides)


@pytest.fixture()
def order(seeded, session):
    user = UserRepository().get_by_email(DEMO_CLIENT_EMAIL)
    address = AddressRepository().add(
        Address(user=user, street="5 Lungă Street", city="Brașov", county="Brașov", postal_code="500035")
    )
    products = ProductRepository()
    apricot = products.get_by_slug("apricot-jam")
    plum = products.get_by_slug("plum-butter")
    created = OrderRepository().add(
        Order(
            user=user,
            address=address,
            status=OrderStatusRepository().get_by_code(OrderStatusCode.PENDING_PAYMENT),
            items=[
                OrderItem(product=apricot, quantity=2, unit_price_cents=2450),
                OrderItem(product=plum, quantity=1, unit_price_cents=2500),
            ],
        )
    )
    session.commit()
    return created


@pytest.fixture()
def fake(app) -> FakeGateway:
    return get_payment_gateway()


def test_payment_gateway_is_an_interface():
    with pytest.raises(TypeError):
        PaymentGateway()


def test_testing_config_selects_the_fake_gateway(app):
    assert isinstance(get_payment_gateway(), FakeGateway)


def test_development_starts_without_stripe_settings_and_selects_stripe(tmp_path):
    app = create_app("development", {"ACTIVITY_LOG_PATH": str(tmp_path / "activity.log"), "STRIPE_SECRET_KEY": ""})

    with app.app_context():
        assert isinstance(get_payment_gateway(), StripeGateway)


def test_production_always_selects_stripe(tmp_path):
    app = production_app(tmp_path)

    with app.app_context():
        assert isinstance(get_payment_gateway(), StripeGateway)


@pytest.mark.parametrize("setting", sorted(PRODUCTION_SETTINGS))
def test_production_refuses_to_start_without_a_required_setting(tmp_path, setting):
    with pytest.raises(RuntimeError, match=setting):
        production_app(tmp_path, **{setting: ""})


def test_unknown_gateway_is_rejected():
    with pytest.raises(ValueError, match="carrier-pigeon"):
        build_gateway({"PAYMENT_GATEWAY": "carrier-pigeon"})


def test_fake_checkout_is_priced_from_the_order(fake, order):
    checkout = fake.create_checkout(order)

    assert fake.checkouts[checkout.reference].amount_cents == 7400
    assert checkout.url.endswith(f"/checkout/success?order={order.id}")


def test_fake_webhook_round_trip(fake, order):
    reference = fake.create_checkout(order).reference

    event = fake.parse_webhook(fake.complete(reference), FAKE_SIGNATURE)

    assert (event.kind, event.reference, event.amount_cents, event.is_paid) == (
        PaymentEventKind.COMPLETED,
        reference,
        7400,
        True,
    )


@pytest.mark.parametrize(
    ("payload", "signature"),
    [(b"{}", FAKE_SIGNATURE), (b"not json", FAKE_SIGNATURE), (b'{"kind": "completed"}', "wrong"), (b'{"kind": "completed"}', None)],
)
def test_fake_webhook_rejects_bad_input(fake, payload, signature):
    with pytest.raises(WebhookError):
        fake.parse_webhook(payload, signature)


def test_fake_expired_checkout_cannot_be_refunded_and_paid_one_cannot_expire(fake, order):
    open_reference = fake.create_checkout(order).reference
    fake.expire_checkout(open_reference)
    assert fake.checkouts[open_reference].status is CheckoutStatus.EXPIRED
    with pytest.raises(PaymentError):
        fake.refund(open_reference)

    paid_reference = fake.create_checkout(order).reference
    fake.complete(paid_reference)
    with pytest.raises(CheckoutAlreadyPaidError):
        fake.expire_checkout(paid_reference)


def test_fake_refund_is_idempotent(fake, order):
    reference = fake.create_checkout(order).reference
    fake.complete(reference)

    fake.refund(reference)
    fake.refund(reference)

    assert fake.refunded == [reference]


def test_fake_can_simulate_an_outage(fake, order):
    fake.is_down = True

    with pytest.raises(PaymentError):
        fake.create_checkout(order)


def test_stripe_checkout_sends_order_prices_in_ron_by_card(order):
    gateway, http = stripe_gateway(session_body())
    before = int(time.time())

    checkout = gateway.create_checkout(order)

    assert (checkout.reference, checkout.url) == ("cs_test_1", SESSION_URL)
    sent = http.requests[0]
    assert sent["method"] == "post" and sent["url"].endswith("/v1/checkout/sessions")
    form = parse_qs(sent["body"])
    assert form["mode"] == ["payment"]
    assert "payment_method_types[0]" not in form
    assert form["client_reference_id"] == [str(order.id)]
    assert form["metadata[order_id]"] == [str(order.id)]
    assert form["success_url"] == [f"{SITE_URL}/checkout/success?order={order.id}"]
    assert form["cancel_url"] == [f"{SITE_URL}/checkout/cancelled?order={order.id}"]
    assert form["line_items[0][price_data][currency]"] == ["ron"]
    assert form["line_items[0][price_data][unit_amount]"] == ["2450"]
    assert form["line_items[0][quantity]"] == ["2"]
    assert form["line_items[0][price_data][product_data][name]"] == ["Apricot Jam"]
    assert form["line_items[1][price_data][unit_amount]"] == ["2500"]
    assert before + 1800 <= int(form["expires_at"][0]) <= before + 86400


def test_stripe_webhook_with_a_valid_signature_is_parsed():
    gateway, _ = stripe_gateway()
    payload = stripe_event("checkout.session.completed")

    event = gateway.parse_webhook(payload, signed(payload))

    assert (event.kind, event.reference, event.amount_cents, event.is_paid) == (
        PaymentEventKind.COMPLETED,
        "cs_test_1",
        5200,
        True,
    )


def test_stripe_webhook_reports_an_unpaid_session():
    gateway, _ = stripe_gateway()
    payload = stripe_event("checkout.session.completed", payment_status="unpaid")

    assert gateway.parse_webhook(payload, signed(payload)).is_paid is False


def test_stripe_webhook_maps_expired_and_ignores_other_events():
    gateway, _ = stripe_gateway()
    expired = stripe_event("checkout.session.expired", payment_status="unpaid")
    other = stripe_event("customer.created")

    assert gateway.parse_webhook(expired, signed(expired)).kind is PaymentEventKind.EXPIRED
    ignored = gateway.parse_webhook(other, signed(other))
    assert ignored.kind is PaymentEventKind.IGNORED
    assert ignored.reference is None


@pytest.mark.parametrize(
    "signature",
    [
        None,
        "",
        "garbage",
        signed(stripe_event("checkout.session.completed"), secret="whsec_other"),
        signed(stripe_event("checkout.session.completed"), timestamp=int(time.time()) - 3600),
    ],
)
def test_stripe_webhook_rejects_a_bad_signature(signature):
    gateway, _ = stripe_gateway()

    with pytest.raises(WebhookError):
        gateway.parse_webhook(stripe_event("checkout.session.completed"), signature)


def test_stripe_webhook_rejects_a_tampered_payload():
    gateway, _ = stripe_gateway()
    signature = signed(stripe_event("checkout.session.completed"))

    with pytest.raises(WebhookError):
        gateway.parse_webhook(stripe_event("checkout.session.completed", amount_total=1), signature)


def test_stripe_webhook_rejects_a_signed_payload_that_is_not_json():
    gateway, _ = stripe_gateway()

    with pytest.raises(WebhookError):
        gateway.parse_webhook(b"not json", signed(b"not json"))


def test_stripe_expire_closes_an_open_session():
    gateway, http = stripe_gateway(session_body("open"), session_body("expired"))

    gateway.expire_checkout("cs_test_1")

    assert http.requests[1]["url"].endswith("/v1/checkout/sessions/cs_test_1/expire")


def test_stripe_expire_leaves_an_expired_session_alone():
    gateway, http = stripe_gateway(session_body("expired"))

    gateway.expire_checkout("cs_test_1")

    assert len(http.requests) == 1


def test_stripe_expire_reports_a_session_that_was_just_paid():
    gateway, http = stripe_gateway(session_body("complete"))

    with pytest.raises(CheckoutAlreadyPaidError):
        gateway.expire_checkout("cs_test_1")

    assert len(http.requests) == 1


def test_stripe_refund_uses_the_payment_intent_and_is_idempotent():
    gateway, http = stripe_gateway(session_body("complete", "pi_1"), (200, {"id": "re_1", "object": "refund"}))

    gateway.refund("cs_test_1")

    sent = http.requests[1]
    assert sent["url"].endswith("/v1/refunds")
    assert parse_qs(sent["body"])["payment_intent"] == ["pi_1"]
    assert sent["headers"]["Idempotency-Key"] == "refund-cs_test_1"


def test_stripe_refund_without_a_payment_is_refused():
    gateway, http = stripe_gateway(session_body("expired"))

    with pytest.raises(PaymentError):
        gateway.refund("cs_test_1")

    assert len(http.requests) == 1


@pytest.mark.parametrize(
    "failure",
    [
        (402, {"error": {"type": "card_error", "message": "secret detail sk_test_key"}}),
        (400, {"error": {"type": "invalid_request_error", "message": "secret detail sk_test_key"}}),
        stripe.APIConnectionError("secret detail sk_test_key", should_retry=False),
    ],
)
def test_stripe_failures_become_a_clean_payment_error(app, failure, activity_log):
    gateway, _ = stripe_gateway(failure)

    with pytest.raises(PaymentError) as caught, app.test_request_context():
        gateway.expire_checkout("cs_test_1")

    assert "secret" not in caught.value.message
    assert "payment_gateway_error" in activity_log()


@pytest.mark.parametrize("call", ["create_checkout", "expire_checkout", "refund"])
def test_stripe_without_a_key_says_payments_are_not_set_up(call):
    gateway = StripeGateway("", WEBHOOK_SECRET, SITE_URL)

    with pytest.raises(PaymentError, match="not set up"):
        getattr(gateway, call)("anything")


def test_stripe_without_a_webhook_secret_says_payments_are_not_set_up():
    gateway = StripeGateway("sk_test_key", "", SITE_URL)

    with pytest.raises(PaymentError, match="not set up"):
        gateway.parse_webhook(b"{}", "signature")


def test_payment_errors_reach_the_client_as_json_without_details(app, seeded):
    gateway, _ = stripe_gateway((400, {"error": {"type": "invalid_request_error", "message": "secret detail sk_test_key"}}))

    @app.get("/api/test/pay")
    def pay():
        gateway.expire_checkout("cs_test_1")
        return {"ok": True}

    with app.app_context():
        response = app.test_client().get("/api/test/pay")

    assert response.status_code == 502
    assert response.get_json() == {"error": PaymentError.message}


def test_webhook_errors_reach_the_client_as_a_400(app, seeded):
    gateway, _ = stripe_gateway()

    @app.get("/api/test/webhook")
    def webhook():
        gateway.parse_webhook(b"{}", "garbage")
        return {"ok": True}

    with app.app_context():
        response = app.test_client().get("/api/test/webhook")

    assert response.status_code == 400
    assert response.get_json() == {"error": WebhookError.message}
