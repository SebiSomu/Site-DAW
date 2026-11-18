import pytest

from app.errors import CheckoutAlreadyPaidError, PaymentError
from app.models import OrderStatusCode, PaymentProvider, PaymentStatus
from app.repositories import OrderRepository, OrderStatusRepository, PaymentRepository, ProductRepository
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD
from app.services.payments import FAKE_SIGNATURE, CheckoutStatus, PaymentEventKind, get_payment_gateway

ADDRESS = {"street": "12 Republicii Street", "city": "Brașov", "county": "Brașov", "postal_code": "500030"}
OTHER_CLIENT = {"email": "ion@example.com", "password": "plum-lover-2026", "first_name": "Ion", "last_name": "Popa"}
ORDERED = {"apricot-jam": 2, "plum-butter": 1}


def jar(slug: str):
    return ProductRepository().get_by_slug(slug, include_inactive=True)


def pay(api, order_id: int):
    return api.post(f"/api/orders/{order_id}/pay")


def payment_of(order_id: int, session):
    session.expire_all()
    return OrderRepository().get(order_id).payment


def order_status(order_id: int, session) -> str:
    session.expire_all()
    return OrderRepository().get(order_id).status.code


def stock_levels(session) -> dict[str, int]:
    session.expire_all()
    return {slug: jar(slug).stock for slug in ORDERED}


def send_webhook(app, payload: bytes, signature: str | None = FAKE_SIGNATURE):
    headers = {} if signature is None else {"Stripe-Signature": signature}
    with app.app_context():
        return app.test_client().post(
            "/api/payments/webhook", data=payload, headers=headers, content_type="application/json"
        )


def cancel(api, order_id: int):
    return api.post(f"/api/orders/{order_id}/cancel")


def set_status(order_id: int, code: OrderStatusCode, session) -> None:
    OrderRepository().get(order_id).status = OrderStatusRepository().get_by_code(code)
    session.commit()


@pytest.fixture()
def fake(app):
    return get_payment_gateway()


@pytest.fixture()
def client_api(api):
    assert api.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD}).status_code == 200
    return api


@pytest.fixture()
def order_total():
    return sum(jar(slug).price_cents * quantity for slug, quantity in ORDERED.items())


@pytest.fixture()
def reference(client_api, order_id, session):
    assert pay(client_api, order_id).status_code == 200
    return payment_of(order_id, session).provider_reference


@pytest.fixture()
def paid(app, order_id, reference, fake, session):
    assert send_webhook(app, fake.complete(reference)).status_code == 200
    assert order_status(order_id, session) == OrderStatusCode.PAID.value
    return reference


@pytest.fixture()
def order_id(client_api):
    address_id = client_api.post("/api/addresses", ADDRESS).get_json()["address"]["id"]
    items = [{"product_id": jar(slug).id, "quantity": quantity} for slug, quantity in ORDERED.items()]
    response = client_api.post("/api/orders", {"address_id": address_id, "items": items})
    assert response.status_code == 201
    return response.get_json()["order"]["id"]


def test_pay_returns_a_checkout_and_records_a_pending_payment(client_api, order_id, order_total, fake, session, activity_log):
    response = pay(client_api, order_id)

    assert response.status_code == 200
    assert response.get_json()["checkout_url"].endswith(f"/checkout/success?order={order_id}")
    payment = payment_of(order_id, session)
    assert (payment.provider, payment.status, payment.amount_cents, payment.paid_at) == (
        PaymentProvider.FAKE.value,
        PaymentStatus.PENDING.value,
        order_total,
        None,
    )
    assert fake.checkouts[payment.provider_reference].amount_cents == order_total
    assert f"payment_started | order={order_id} amount_cents={order_total}" in activity_log()


def test_pay_charges_the_price_at_purchase_time(client_api, order_id, order_total, fake, session):
    jar("apricot-jam").price_cents += 1000
    session.commit()

    assert pay(client_api, order_id).status_code == 200

    payment = payment_of(order_id, session)
    assert payment.amount_cents == order_total
    assert fake.checkouts[payment.provider_reference].amount_cents == order_total


def test_pay_requires_login(api):
    assert pay(api, 1).status_code == 401


def test_pay_requires_the_csrf_token(client_api, order_id, fake):
    with client_api.client.application.app_context():
        response = client_api.client.post(f"/api/orders/{order_id}/pay")

    assert response.status_code == 400
    assert fake.checkouts == {}


def test_another_clients_order_cannot_be_paid(new_api, order_id, fake, session):
    other = new_api()
    assert other.post("/api/auth/register", OTHER_CLIENT).status_code == 201

    assert pay(other, order_id).status_code == 404
    assert pay(other, 99999).status_code == 404
    assert fake.checkouts == {}
    assert payment_of(order_id, session) is None


@pytest.mark.parametrize(
    "code",
    [
        OrderStatusCode.PAID,
        OrderStatusCode.CONFIRMED,
        OrderStatusCode.SHIPPED,
        OrderStatusCode.DELIVERED,
        OrderStatusCode.CANCELLED,
    ],
)
def test_only_an_order_awaiting_payment_can_be_paid(client_api, order_id, fake, session, code):
    set_status(order_id, code, session)

    response = pay(client_api, order_id)

    assert response.status_code == 409
    assert response.get_json()["error"] == "This order is not waiting for payment."
    assert fake.checkouts == {}


def test_pay_rechecks_stock(client_api, order_id, fake, session):
    jar("apricot-jam").stock = 1
    session.commit()

    response = pay(client_api, order_id)

    assert response.status_code == 409
    assert response.get_json()["error"].startswith("Only 1 left of Apricot Jam.")
    assert fake.checkouts == {}
    assert payment_of(order_id, session) is None


def test_pay_refuses_a_jar_no_longer_for_sale(client_api, order_id, fake, session):
    jar("plum-butter").is_active = False
    session.commit()

    response = pay(client_api, order_id)

    assert response.status_code == 409
    assert "no longer for sale" in response.get_json()["error"]
    assert fake.checkouts == {}


def test_retry_expires_the_previous_session_and_replaces_the_reference(client_api, order_id, fake, session):
    assert pay(client_api, order_id).status_code == 200
    first = payment_of(order_id, session).provider_reference

    assert pay(client_api, order_id).status_code == 200

    payment = payment_of(order_id, session)
    assert payment.provider_reference != first
    assert payment.status == PaymentStatus.PENDING.value
    assert fake.checkouts[first].status is CheckoutStatus.EXPIRED
    assert fake.checkouts[payment.provider_reference].status is CheckoutStatus.OPEN
    assert PaymentRepository().count() == 1


def test_retry_after_a_failed_session_starts_a_new_one_without_expiring_again(
    client_api, order_id, fake, session, monkeypatch
):
    assert pay(client_api, order_id).status_code == 200
    payment = payment_of(order_id, session)
    first = payment.provider_reference
    fake.expire_event(first)
    payment.status = PaymentStatus.FAILED.value
    session.commit()
    expired = []
    monkeypatch.setattr(fake, "expire_checkout", expired.append)

    response = pay(client_api, order_id)

    assert response.status_code == 200
    assert payment_of(order_id, session).provider_reference != first
    assert expired == []


def test_retry_of_a_session_that_was_just_paid_is_refused(client_api, order_id, fake, session):
    assert pay(client_api, order_id).status_code == 200
    reference = payment_of(order_id, session).provider_reference
    fake.complete(reference)

    response = pay(client_api, order_id)

    assert response.status_code == 409
    assert response.get_json() == {"error": CheckoutAlreadyPaidError.message}
    assert payment_of(order_id, session).provider_reference == reference
    assert len(fake.checkouts) == 1


def test_gateway_outage_keeps_the_order_and_allows_a_retry(client_api, order_id, fake, session):
    fake.is_down = True

    response = pay(client_api, order_id)

    assert response.status_code == 502
    assert response.get_json() == {"error": PaymentError.message}
    order = client_api.get(f"/api/orders/{order_id}").get_json()["order"]
    assert order["status"]["code"] == OrderStatusCode.PENDING_PAYMENT.value
    assert payment_of(order_id, session) is None

    fake.is_down = False
    assert pay(client_api, order_id).status_code == 200


def test_gateway_outage_on_retry_keeps_the_open_session(client_api, order_id, fake, session):
    assert pay(client_api, order_id).status_code == 200
    reference = payment_of(order_id, session).provider_reference
    fake.is_down = True

    assert pay(client_api, order_id).status_code == 502

    payment = payment_of(order_id, session)
    assert (payment.provider_reference, payment.status) == (reference, PaymentStatus.PENDING.value)
    assert fake.checkouts[reference].status is CheckoutStatus.OPEN


def test_paid_webhook_marks_the_order_paid_and_takes_the_stock(app, order_id, reference, fake, session, activity_log):
    before = stock_levels(session)

    response = send_webhook(app, fake.complete(reference))

    assert response.status_code == 200
    assert order_status(order_id, session) == OrderStatusCode.PAID.value
    payment = payment_of(order_id, session)
    assert payment.status == PaymentStatus.SUCCEEDED.value
    assert payment.paid_at is not None
    assert stock_levels(session) == {slug: before[slug] - quantity for slug, quantity in ORDERED.items()}
    assert f"payment_succeeded | order={order_id}" in activity_log()


def test_paid_order_makes_its_jars_reviewable(app, client_api, reference, fake):
    send_webhook(app, fake.complete(reference))

    eligibility = client_api.get(f"/api/products/{jar('apricot-jam').id}/reviews/eligibility")

    assert eligibility.get_json() == {"can_review": True}


@pytest.mark.parametrize("signature", ["wrong", None])
def test_webhook_with_a_bad_signature_is_rejected_and_logged(app, order_id, reference, fake, session, activity_log, signature):
    before = stock_levels(session)

    response = send_webhook(app, fake.complete(reference), signature)

    assert response.status_code == 400
    assert response.get_json() == {"error": "This payment notification could not be verified."}
    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value
    assert stock_levels(session) == before
    assert "webhook_rejected" in activity_log()


def test_resent_event_takes_the_stock_only_once(app, order_id, reference, fake, session):
    before = stock_levels(session)
    payload = fake.complete(reference)

    assert send_webhook(app, payload).status_code == 200
    assert send_webhook(app, payload).status_code == 200

    assert stock_levels(session) == {slug: before[slug] - quantity for slug, quantity in ORDERED.items()}
    assert fake.refunded == []


def test_oversold_jar_is_refunded_and_the_order_cancelled(app, order_id, reference, fake, session, activity_log):
    jar("apricot-jam").stock = 1
    session.commit()
    before = stock_levels(session)
    payload = fake.complete(reference)

    assert send_webhook(app, payload).status_code == 200
    assert send_webhook(app, payload).status_code == 200

    assert order_status(order_id, session) == OrderStatusCode.CANCELLED.value
    assert payment_of(order_id, session).status == PaymentStatus.REFUNDED.value
    assert stock_levels(session) == before
    assert fake.refunded == [reference]
    assert f"payment_refunded | order={order_id} reason=a jar sold out" in activity_log()


def test_amount_mismatch_is_refunded_and_never_marked_paid(app, order_id, order_total, reference, fake, session, activity_log):
    before = stock_levels(session)
    fake.complete(reference)
    payload = fake.event_payload(PaymentEventKind.COMPLETED, reference, order_total - 100, is_paid=True)

    assert send_webhook(app, payload).status_code == 200

    assert order_status(order_id, session) == OrderStatusCode.CANCELLED.value
    assert payment_of(order_id, session).status == PaymentStatus.REFUNDED.value
    assert stock_levels(session) == before
    assert "amount mismatch" in activity_log()


def test_payment_for_a_cancelled_order_is_refunded(app, order_id, reference, fake, session):
    before = stock_levels(session)
    set_status(order_id, OrderStatusCode.CANCELLED, session)

    assert send_webhook(app, fake.complete(reference)).status_code == 200

    assert payment_of(order_id, session).status == PaymentStatus.REFUNDED.value
    assert order_status(order_id, session) == OrderStatusCode.CANCELLED.value
    assert stock_levels(session) == before
    assert fake.refunded == [reference]


def test_unknown_session_is_acknowledged_and_logged(app, order_id, reference, fake, session, activity_log):
    payload = fake.event_payload(PaymentEventKind.COMPLETED, "cs_unknown", 100, is_paid=True)

    assert send_webhook(app, payload).status_code == 200

    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value
    assert "webhook_unknown_session | reference=cs_unknown" in activity_log()


def test_completed_but_unpaid_session_changes_nothing(app, order_id, order_total, reference, fake, session):
    payload = fake.event_payload(PaymentEventKind.COMPLETED, reference, order_total, is_paid=False)

    assert send_webhook(app, payload).status_code == 200

    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value
    assert payment_of(order_id, session).status == PaymentStatus.PENDING.value


def test_expired_session_fails_the_payment_and_keeps_the_order_open(app, client_api, order_id, reference, fake, session, activity_log):
    assert send_webhook(app, fake.expire_event(reference)).status_code == 200

    assert payment_of(order_id, session).status == PaymentStatus.FAILED.value
    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value
    assert f"payment_failed | order={order_id}" in activity_log()
    assert pay(client_api, order_id).status_code == 200


def test_other_events_are_acknowledged_and_ignored(app, order_id, reference, fake, session):
    assert send_webhook(app, fake.event_payload(PaymentEventKind.IGNORED)).status_code == 200

    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value


def test_failed_refund_returns_an_error_so_the_event_is_retried(app, order_id, reference, fake, session):
    jar("apricot-jam").stock = 1
    session.commit()
    payload = fake.complete(reference)
    fake.is_down = True

    assert send_webhook(app, payload).status_code == 502
    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value
    assert payment_of(order_id, session).status == PaymentStatus.PENDING.value

    fake.is_down = False
    assert send_webhook(app, payload).status_code == 200
    assert order_status(order_id, session) == OrderStatusCode.CANCELLED.value
    assert fake.refunded == [reference]


def test_cancelling_an_unpaid_order_closes_its_open_session(client_api, order_id, reference, fake, session):
    response = cancel(client_api, order_id)

    assert response.status_code == 200
    assert response.get_json()["order"]["status"]["code"] == OrderStatusCode.CANCELLED.value
    assert fake.checkouts[reference].status is CheckoutStatus.EXPIRED
    assert payment_of(order_id, session).status == PaymentStatus.FAILED.value
    assert fake.refunded == []


def test_cancelling_an_unpaid_order_whose_session_was_just_paid_is_refused(client_api, order_id, reference, fake, session):
    fake.complete(reference)

    response = cancel(client_api, order_id)

    assert response.status_code == 409
    assert response.get_json() == {"error": CheckoutAlreadyPaidError.message}
    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value


def test_cancelling_an_unpaid_order_while_the_gateway_is_down_changes_nothing(client_api, order_id, reference, fake, session):
    fake.is_down = True

    assert cancel(client_api, order_id).status_code == 502

    assert order_status(order_id, session) == OrderStatusCode.PENDING_PAYMENT.value
    assert payment_of(order_id, session).status == PaymentStatus.PENDING.value
    assert fake.checkouts[reference].status is CheckoutStatus.OPEN


@pytest.mark.parametrize("code", [OrderStatusCode.PAID, OrderStatusCode.CONFIRMED])
def test_cancelling_a_paid_order_refunds_it_and_restores_the_stock_once(
    client_api, order_id, paid, fake, session, activity_log, code
):
    set_status(order_id, code, session)
    before = stock_levels(session)

    response = cancel(client_api, order_id)

    assert response.status_code == 200
    assert order_status(order_id, session) == OrderStatusCode.CANCELLED.value
    assert payment_of(order_id, session).status == PaymentStatus.REFUNDED.value
    assert fake.refunded == [paid]
    restored = {slug: before[slug] + quantity for slug, quantity in ORDERED.items()}
    assert stock_levels(session) == restored
    assert f"payment_refunded | order={order_id} reason=cancelled by the client" in activity_log()

    assert cancel(client_api, order_id).status_code == 409
    assert stock_levels(session) == restored
    assert fake.refunded == [paid]


def test_failed_refund_leaves_a_paid_order_as_it_was(client_api, order_id, paid, fake, session):
    before = stock_levels(session)
    fake.is_down = True

    response = cancel(client_api, order_id)

    assert response.status_code == 502
    assert response.get_json() == {"error": PaymentError.message}
    assert order_status(order_id, session) == OrderStatusCode.PAID.value
    assert payment_of(order_id, session).status == PaymentStatus.SUCCEEDED.value
    assert stock_levels(session) == before
    assert fake.refunded == []


@pytest.mark.parametrize("code", [OrderStatusCode.SHIPPED, OrderStatusCode.DELIVERED])
def test_a_shipped_paid_order_cannot_be_cancelled_or_refunded(client_api, order_id, paid, fake, session, code):
    set_status(order_id, code, session)
    before = stock_levels(session)

    assert cancel(client_api, order_id).status_code == 409

    assert payment_of(order_id, session).status == PaymentStatus.SUCCEEDED.value
    assert stock_levels(session) == before
    assert fake.refunded == []


def test_payment_status_changes_only_from_an_allowed_status(order_id, paid, session):
    payment = payment_of(order_id, session)
    payments = PaymentRepository()

    assert payments.change_status(payment.id, {PaymentStatus.SUCCEEDED.value}, PaymentStatus.REFUNDED.value) is True
    assert payments.change_status(payment.id, {PaymentStatus.SUCCEEDED.value}, PaymentStatus.REFUNDED.value) is False
    session.rollback()


def test_stock_is_only_taken_when_enough_is_left(seeded, session):
    products = ProductRepository()
    product = jar("apricot-jam")
    stock = product.stock

    assert products.take_stock(product.id, stock + 1) is False
    assert products.take_stock(product.id, stock) is True
    products.restore_stock(product.id, 2)
    session.commit()

    assert stock_levels(session)["apricot-jam"] == 2


def test_concurrent_duplicate_event_is_stopped_by_the_conditional_status_change(
    app, order_id, reference, fake, session, activity_log, monkeypatch
):
    before = stock_levels(session)
    payload = fake.complete(reference)
    assert send_webhook(app, payload).status_code == 200
    set_status(order_id, OrderStatusCode.PENDING_PAYMENT, session)
    monkeypatch.setattr("app.services.payment_service.SETTLED_PAYMENTS", frozenset())

    assert send_webhook(app, payload).status_code == 200

    assert stock_levels(session) == {slug: before[slug] - quantity for slug, quantity in ORDERED.items()}
    assert f"webhook_duplicate | order={order_id}" in activity_log()
