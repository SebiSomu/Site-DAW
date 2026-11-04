import pytest

from app.models import OrderStatusCode
from app.repositories import OrderRepository, OrderStatusRepository, ProductRepository
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD

NEW_ADDRESS = {"street": "5 Lungă Street", "city": "Brașov", "county": "Brașov", "postal_code": "500035"}
OTHER_CLIENT = {"email": "ana@example.com", "password": "jam-lover-2026", "first_name": "Ana", "last_name": "Pop"}


def product(slug: str):
    return ProductRepository().get_by_slug(slug)


def set_status(order_id: int, code: OrderStatusCode, session) -> None:
    OrderRepository().get(order_id).status = OrderStatusRepository().get_by_code(code)
    session.commit()


@pytest.fixture()
def client_api(api):
    assert api.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD}).status_code == 200
    return api


@pytest.fixture()
def other_api(new_api):
    other = new_api()
    assert other.post("/api/auth/register", OTHER_CLIENT).status_code == 201
    return other


@pytest.fixture()
def address_id(client_api):
    return client_api.post("/api/addresses", NEW_ADDRESS).get_json()["address"]["id"]


@pytest.fixture()
def placed_order(client_api, address_id):
    items = [{"product_id": product("strawberry-jam").id, "quantity": 2}]
    response = client_api.post("/api/orders", {"address_id": address_id, "items": items})
    assert response.status_code == 201
    return response.get_json()["order"]


def test_cart_total_uses_server_prices_and_merges_repeated_jars(api):
    jar = product("strawberry-jam")
    body = {"items": [{"product_id": jar.id, "quantity": 1}, {"product_id": jar.id, "quantity": 2}]}

    response = api.post("/api/cart/validate", body)

    assert response.status_code == 200
    summary = response.get_json()
    assert summary["lines"][0]["quantity"] == 3
    assert summary["total_cents"] == 3 * jar.price_cents


def test_cart_rejects_a_client_supplied_price(api):
    jar = product("strawberry-jam")
    body = {"items": [{"product_id": jar.id, "quantity": 1, "price_cents": 1}]}

    response = api.post("/api/cart/validate", body)

    assert response.status_code == 400
    assert response.get_json()["error"].startswith("items.0.price_cents:")


def test_cart_flags_unknown_and_inactive_jars_and_too_many_jars(api, session):
    hidden = product("apricot-jam")
    hidden.is_active = False
    session.commit()
    jar = product("strawberry-jam")
    items = [
        {"product_id": 99999, "quantity": 1},
        {"product_id": hidden.id, "quantity": 1},
        {"product_id": jar.id, "quantity": jar.stock + 1},
    ]

    summary = api.post("/api/cart/validate", {"items": items}).get_json()

    assert summary["missing_product_ids"] == [99999, hidden.id]
    assert summary["lines"][0]["is_available"] is False
    assert summary["total_cents"] == 0


@pytest.mark.parametrize("quantity", [0, -1, 100])
def test_cart_rejects_quantities_out_of_range(api, quantity):
    jar = product("strawberry-jam")

    response = api.post("/api/cart/validate", {"items": [{"product_id": jar.id, "quantity": quantity}]})

    assert response.status_code == 400


def test_guest_session_endpoint_returns_null_user(api):
    response = api.get("/api/auth/session")

    assert response.status_code == 200
    assert response.get_json() == {"user": None}


def test_session_endpoint_returns_logged_in_user(client_api):
    assert client_api.get("/api/auth/session").get_json()["user"]["email"] == DEMO_CLIENT_EMAIL


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", "/api/addresses"),
        ("post", "/api/addresses"),
        ("get", "/api/orders"),
        ("post", "/api/orders"),
        ("get", "/api/orders/1"),
        ("post", "/api/orders/1/cancel"),
        ("get", "/api/products/1/reviews/eligibility"),
        ("post", "/api/products/1/reviews"),
    ],
)
def test_shop_routes_require_login(api, method, url):
    assert getattr(api, method)(url).status_code == 401


def test_address_is_added_listed_and_archived(client_api, activity_log):
    created = client_api.post("/api/addresses", NEW_ADDRESS)

    assert created.status_code == 201
    address = created.get_json()["address"]
    assert address["one_line"] == "5 Lungă Street, Brașov, Brașov County, 500035"
    assert address["id"] in [item["id"] for item in client_api.get("/api/addresses").get_json()["addresses"]]
    assert client_api.delete(f"/api/addresses/{address['id']}").status_code == 204
    assert address["id"] not in [item["id"] for item in client_api.get("/api/addresses").get_json()["addresses"]]
    assert "address_added" in activity_log() and "address_archived" in activity_log()


@pytest.mark.parametrize("overrides", [{"postal_code": "12"}, {"street": "   "}, {"user_id": 1}])
def test_address_input_is_validated(client_api, overrides):
    assert client_api.post("/api/addresses", {**NEW_ADDRESS, **overrides}).status_code == 400


def test_address_of_another_client_cannot_be_archived_or_used(other_api, address_id):
    jar = product("strawberry-jam")

    assert other_api.delete(f"/api/addresses/{address_id}").status_code == 404
    response = other_api.post("/api/orders", {"address_id": address_id, "items": [{"product_id": jar.id, "quantity": 1}]})
    assert response.status_code == 404


def test_order_is_placed_at_server_price_and_awaits_payment(placed_order, activity_log):
    jar = product("strawberry-jam")

    assert placed_order["status"]["code"] == OrderStatusCode.PENDING_PAYMENT.value
    assert placed_order["total_cents"] == 2 * jar.price_cents
    assert placed_order["items"][0]["unit_price_cents"] == jar.price_cents
    assert placed_order["is_cancellable"] is True
    assert f"order_created | order={placed_order['id']}" in activity_log()


def test_order_keeps_its_price_when_the_jar_gets_more_expensive(client_api, placed_order, session):
    jar = product("strawberry-jam")
    original = jar.price_cents
    jar.price_cents = original + 500
    session.commit()

    order = client_api.get(f"/api/orders/{placed_order['id']}").get_json()["order"]

    assert order["items"][0]["unit_price_cents"] == original


def test_order_over_stock_is_rejected(client_api, address_id):
    jar = product("strawberry-jam")
    items = [{"product_id": jar.id, "quantity": jar.stock + 1}]

    response = client_api.post("/api/orders", {"address_id": address_id, "items": items})

    assert response.status_code == 409
    assert jar.name in response.get_json()["error"]


def test_order_for_a_jar_no_longer_sold_is_rejected(client_api, address_id, session):
    jar = product("strawberry-jam")
    jar.is_active = False
    session.commit()

    response = client_api.post("/api/orders", {"address_id": address_id, "items": [{"product_id": jar.id, "quantity": 1}]})

    assert response.status_code == 409


def test_empty_order_is_rejected(client_api, address_id):
    assert client_api.post("/api/orders", {"address_id": address_id, "items": []}).status_code == 400


def test_order_notes_are_stored_as_plain_text(client_api, address_id):
    jar = product("strawberry-jam")
    notes = "<script>alert(1)</script>Ring <b>twice</b> & wait"
    body = {"address_id": address_id, "items": [{"product_id": jar.id, "quantity": 1}], "notes": notes}

    assert client_api.post("/api/orders", body).get_json()["order"]["notes"] == "Ring twice & wait"


def test_client_only_sees_their_own_orders(client_api, other_api, placed_order):
    assert other_api.get(f"/api/orders/{placed_order['id']}").status_code == 404
    assert other_api.post(f"/api/orders/{placed_order['id']}/cancel").status_code == 404
    assert other_api.get("/api/orders").get_json()["orders"] == []
    assert placed_order["id"] in [order["id"] for order in client_api.get("/api/orders").get_json()["orders"]]


def test_cancel_is_allowed_before_shipping(client_api, placed_order, activity_log):
    response = client_api.post(f"/api/orders/{placed_order['id']}/cancel")

    assert response.status_code == 200
    assert response.get_json()["order"]["status"]["code"] == OrderStatusCode.CANCELLED.value
    assert f"order_cancelled | order={placed_order['id']}" in activity_log()


@pytest.mark.parametrize("code", [OrderStatusCode.SHIPPED, OrderStatusCode.DELIVERED, OrderStatusCode.CANCELLED])
def test_cancel_is_refused_once_shipped_or_already_cancelled(client_api, placed_order, session, code):
    set_status(placed_order["id"], code, session)

    assert client_api.post(f"/api/orders/{placed_order['id']}/cancel").status_code == 409


def test_review_needs_a_purchase(other_api):
    jar = product("strawberry-jam")

    assert other_api.get(f"/api/products/{jar.id}/reviews/eligibility").get_json() == {"can_review": False}
    assert other_api.post(f"/api/products/{jar.id}/reviews", {"rating": 5}).status_code == 403


def test_unpaid_order_does_not_count_as_a_purchase(client_api, placed_order):
    jar = product("strawberry-jam")

    assert client_api.post(f"/api/products/{jar.id}/reviews", {"rating": 5}).status_code == 403


def test_review_is_posted_once_and_stored_as_plain_text(client_api, placed_order, session, activity_log):
    jar = product("strawberry-jam")
    set_status(placed_order["id"], OrderStatusCode.DELIVERED, session)
    url = f"/api/products/{jar.id}/reviews"
    assert client_api.get(f"{url}/eligibility").get_json() == {"can_review": True}

    response = client_api.post(url, {"rating": 4, "comment": "<script>alert(1)</script>Lovely & <b>sweet</b>"})

    assert response.status_code == 201
    assert response.get_json()["review"]["comment"] == "Lovely & sweet"
    assert client_api.get(f"{url}/eligibility").get_json() == {"can_review": False}
    assert client_api.post(url, {"rating": 1}).status_code == 409
    assert "review_posted" in activity_log()
    assert client_api.get(f"/api/products/{jar.slug}").get_json()["product"]["average_rating"] == 4


@pytest.mark.parametrize("rating", [0, 6])
def test_review_rating_is_validated(client_api, rating):
    jar = product("apricot-jam")

    assert client_api.post(f"/api/products/{jar.id}/reviews", {"rating": rating}).status_code == 400


def test_review_of_an_unknown_jar_is_not_found(client_api):
    assert client_api.post("/api/products/99999/reviews", {"rating": 5}).status_code == 404


def test_demo_client_starts_with_no_address_and_no_orders(client_api):
    assert client_api.get("/api/addresses").get_json() == {"addresses": []}
    assert client_api.get("/api/orders").get_json() == {"orders": []}
