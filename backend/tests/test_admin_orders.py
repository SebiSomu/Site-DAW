import pytest

from app.models import ContactMessage, OrderStatusCode
from app.repositories import OrderRepository, OrderStatusRepository, ProductRepository
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD
from app.services.payments import FAKE_SIGNATURE, CheckoutStatus, get_payment_gateway

ADDRESS = {"street": "12 Republicii Street", "city": "Brașov", "county": "Brașov", "postal_code": "500030"}
OTHER_CLIENT = {"email": "ion@example.com", "password": "plum-lover-2026", "first_name": "Ion", "last_name": "Popa"}


def stock(slug: str, session) -> int:
    session.expire_all()
    return ProductRepository().get_by_slug(slug, include_inactive=True).stock


def jar_id(slug: str) -> int:
    return ProductRepository().get_by_slug(slug, include_inactive=True).id


def set_status(order_id: int, code: OrderStatusCode, session) -> None:
    OrderRepository().get(order_id).status = OrderStatusRepository().get_by_code(code)
    session.commit()


def change(admin_api, order_id: int, status: str):
    return admin_api.patch(f"/api/admin/orders/{order_id}/status", {"status": status})


@pytest.fixture()
def fake(app):
    return get_payment_gateway()


@pytest.fixture()
def admin_api(new_api):
    admin = new_api()
    assert admin.post("/api/auth/login", {"email": "admin@example.com", "password": "Test-Password-123"}).status_code == 200
    return admin


@pytest.fixture()
def client_api(api):
    assert api.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD}).status_code == 200
    return api


@pytest.fixture()
def place(client_api):
    address_id = client_api.post("/api/addresses", ADDRESS).get_json()["address"]["id"]

    def place_order(slug: str = "apricot-jam", quantity: int = 2) -> int:
        body = {"address_id": address_id, "items": [{"product_id": jar_id(slug), "quantity": quantity}]}
        response = client_api.post("/api/orders", body)
        assert response.status_code == 201
        return response.get_json()["order"]["id"]

    return place_order


@pytest.fixture()
def pay(app, client_api, fake, session):
    def pay_order(order_id: int) -> str:
        assert client_api.post(f"/api/orders/{order_id}/pay").status_code == 200
        session.expire_all()
        reference = OrderRepository().get(order_id).payment.provider_reference
        with app.app_context():
            response = app.test_client().post(
                "/api/payments/webhook",
                data=fake.complete(reference),
                headers={"Stripe-Signature": FAKE_SIGNATURE},
                content_type="application/json",
            )
        assert response.status_code == 200
        return reference

    return pay_order


@pytest.fixture()
def paid_order(place, pay):
    order_id = place()
    pay(order_id)
    return order_id


ADMIN_ROUTES = [
    ("get", "/api/admin/summary"),
    ("get", "/api/admin/orders"),
    ("get", "/api/admin/orders/1"),
    ("patch", "/api/admin/orders/1/status"),
]


def call(api, method, url):
    return api.get(url) if method == "get" else api.patch(url, {"status": "confirmed"})


@pytest.mark.parametrize(("method", "url"), ADMIN_ROUTES)
def test_guest_is_asked_to_log_in(new_api, method, url):
    assert call(new_api(), method, url).status_code == 401


@pytest.mark.parametrize(("method", "url"), ADMIN_ROUTES)
def test_client_is_refused(client_api, method, url):
    assert call(client_api, method, url).status_code == 403


def test_admin_sees_every_clients_orders_newest_first(admin_api, place, new_api):
    first = place()
    other = new_api()
    assert other.post("/api/auth/register", OTHER_CLIENT).status_code == 201
    address_id = other.post("/api/addresses", ADDRESS).get_json()["address"]["id"]
    second = other.post(
        "/api/orders", {"address_id": address_id, "items": [{"product_id": jar_id("plum-butter"), "quantity": 1}]}
    ).get_json()["order"]["id"]

    orders = admin_api.get("/api/admin/orders").get_json()["orders"]

    assert [order["id"] for order in orders] == [second, first]
    assert orders[0]["customer"]["name"] == "Ion Popa"
    assert orders[1]["customer"]["email"] == DEMO_CLIENT_EMAIL


def test_orders_are_filtered_by_status(admin_api, place, paid_order):
    waiting = place("plum-butter", 1)

    paid = admin_api.get("/api/admin/orders?status=paid").get_json()["orders"]
    unpaid = admin_api.get("/api/admin/orders?status=pending_payment").get_json()["orders"]

    assert [order["id"] for order in paid] == [paid_order]
    assert [order["id"] for order in unpaid] == [waiting]
    assert admin_api.get("/api/admin/orders?status=lost").status_code == 400


def test_order_detail_shows_the_customer_payment_and_next_steps(admin_api, paid_order):
    order = admin_api.get(f"/api/admin/orders/{paid_order}").get_json()["order"]

    assert order["status"]["code"] == "paid"
    assert order["payment_status"] == "succeeded"
    assert order["paid_at"] is not None
    assert order["ships_to"].startswith("12 Republicii Street, Brașov")
    assert order["items"][0]["product_slug"] == "apricot-jam"
    assert [status["code"] for status in order["next_statuses"]] == ["confirmed", "cancelled"]


def test_unknown_order_is_404(admin_api):
    assert admin_api.get("/api/admin/orders/9999").status_code == 404
    assert change(admin_api, 9999, "confirmed").status_code == 404


def test_admin_moves_a_paid_order_all_the_way_to_delivered(admin_api, paid_order, activity_log):
    for status, next_codes in (("confirmed", ["shipped", "cancelled"]), ("shipped", ["delivered"]), ("delivered", [])):
        response = change(admin_api, paid_order, status)

        assert response.status_code == 200
        order = response.get_json()["order"]
        assert order["status"]["code"] == status
        assert [step["code"] for step in order["next_statuses"]] == next_codes
        assert f"order_status_changed | order={paid_order} " in activity_log()
    assert "from=shipped to=delivered by=admin" in activity_log()


@pytest.mark.parametrize(
    ("start", "target"),
    [
        (OrderStatusCode.PAID, "shipped"),
        (OrderStatusCode.PAID, "delivered"),
        (OrderStatusCode.PAID, "paid"),
        (OrderStatusCode.SHIPPED, "cancelled"),
        (OrderStatusCode.DELIVERED, "shipped"),
        (OrderStatusCode.CANCELLED, "confirmed"),
    ],
)
def test_steps_cannot_be_skipped_or_undone(admin_api, paid_order, session, start, target):
    set_status(paid_order, start, session)

    response = change(admin_api, paid_order, target)

    assert response.status_code == 409
    assert "cannot be marked" in response.get_json()["error"]


def test_only_the_payment_webhook_can_mark_an_order_paid(admin_api, place):
    response = change(admin_api, place(), "paid")

    assert response.status_code == 409


@pytest.mark.parametrize("body", [{"status": "lost"}, {}, {"status": "confirmed", "extra": 1}])
def test_status_change_is_validated(admin_api, paid_order, body):
    assert admin_api.patch(f"/api/admin/orders/{paid_order}/status", body).status_code == 400


def test_admin_cancels_an_unpaid_order_and_closes_its_payment_page(admin_api, client_api, place, fake, session):
    order_id = place()
    assert client_api.post(f"/api/orders/{order_id}/pay").status_code == 200
    session.expire_all()
    reference = OrderRepository().get(order_id).payment.provider_reference

    response = change(admin_api, order_id, "cancelled")

    assert response.status_code == 200
    assert response.get_json()["order"]["status"]["code"] == "cancelled"
    assert fake.checkouts[reference].status is CheckoutStatus.EXPIRED


def test_admin_cancelling_a_paid_order_refunds_it_and_restocks_once(admin_api, paid_order, fake, session, activity_log):
    before = stock("apricot-jam", session)

    response = change(admin_api, paid_order, "cancelled")

    order = response.get_json()["order"]
    assert (order["status"]["code"], order["payment_status"]) == ("cancelled", "refunded")
    assert stock("apricot-jam", session) == before + 2
    assert len(fake.refunded) == 1
    assert f"order_cancelled | order={paid_order} by=admin" in activity_log()
    assert change(admin_api, paid_order, "cancelled").status_code == 409
    assert stock("apricot-jam", session) == before + 2


def test_failed_refund_leaves_the_order_as_it_was(admin_api, paid_order, fake, session):
    fake.is_down = True

    response = change(admin_api, paid_order, "cancelled")

    assert response.status_code == 502
    session.expire_all()
    assert OrderRepository().get(paid_order).status.code == "paid"


def test_dashboard_summary_counts_only_what_was_really_paid(admin_api, place, paid_order, session):
    place("plum-butter", 1)
    cancelled = place("raspberry-jam", 1)
    set_status(cancelled, OrderStatusCode.CANCELLED, session)
    session.add(ContactMessage(name="Ana", email="ana@example.com", subject="Hello", message="Lovely jam"))
    session.commit()
    apricot_price = ProductRepository().get_by_slug("apricot-jam").price_cents

    summary = admin_api.get("/api/admin/summary").get_json()

    assert summary["revenue_cents"] == 2 * apricot_price
    assert (summary["paid_orders"], summary["orders_to_send"], summary["awaiting_payment"]) == (1, 1, 1)
    assert summary["messages"] == 1
    counts = {row["code"]: row["count"] for row in summary["orders_by_status"]}
    assert counts == {"pending_payment": 1, "paid": 1, "confirmed": 0, "shipped": 0, "delivered": 0, "cancelled": 1}
    assert [row["code"] for row in summary["orders_by_status"]][0] == "pending_payment"
    assert summary["low_stock"][0]["slug"] == "rosehip-jam"
    assert all(jar["stock"] <= 5 for jar in summary["low_stock"])
    assert [order["id"] for order in summary["recent_orders"]][-1] == paid_order


def test_dashboard_summary_of_an_empty_shop(admin_api):
    summary = admin_api.get("/api/admin/summary").get_json()

    assert (summary["revenue_cents"], summary["paid_orders"], summary["recent_orders"]) == (0, 0, [])


def test_an_order_moved_by_someone_else_a_moment_ago_is_refused(admin_api, paid_order, session, monkeypatch, activity_log):
    monkeypatch.setattr(OrderRepository, "change_status", lambda self, order_id, current, target: False)

    response = change(admin_api, paid_order, "confirmed")

    assert response.status_code == 409
    assert "changed a moment ago" in response.get_json()["error"]
    session.expire_all()
    assert OrderRepository().get(paid_order).status.code == OrderStatusCode.PAID.value
    assert "order_status_changed" not in activity_log()
