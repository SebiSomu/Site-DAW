import pytest

from app.errors import CheckoutAlreadyPaidError, PaymentError
from app.models import OrderStatusCode, PaymentProvider, PaymentStatus
from app.repositories import OrderRepository, OrderStatusRepository, PaymentRepository, ProductRepository
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD
from app.services.payments import CheckoutStatus, get_payment_gateway

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
