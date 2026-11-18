import io
import os

import pytest
from PIL import Image

from app.models import Product
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD

NEW_JAR = {
    "name": "Dulceață de Gutui Veche",
    "category_slug": "preserves",
    "description": "Old-style quince preserve from a Brașov recipe.",
    "price_cents": 3150,
    "weight_grams": 370,
    "stock": 12,
    "ingredients": ["Quinces", "sugar", "quinces", " lemon "],
}


def photo(image_format="JPEG", size=(800, 600)):
    output = io.BytesIO()
    Image.new("RGB", size, (200, 120, 40)).save(output, image_format)
    return output.getvalue()


@pytest.fixture()
def admin_api(api):
    assert api.post("/api/auth/login", {"email": "admin@example.com", "password": "Test-Password-123"}).status_code == 200
    return api


@pytest.fixture()
def client_api(new_api):
    client = new_api()
    assert client.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD}).status_code == 200
    return client


@pytest.fixture()
def created(admin_api):
    response = admin_api.post("/api/admin/products", NEW_JAR)
    assert response.status_code == 201
    return response.get_json()["product"]


def upload(admin_api, product_id, data=None, name="jar.jpg", alt_text="A jar of quince preserve"):
    form = {"photo": (io.BytesIO(data if data is not None else photo()), name)}
    if alt_text is not None:
        form["alt_text"] = alt_text
    return admin_api.post_form(f"/api/admin/products/{product_id}/images", form)


def upload_folder(app):
    folder = app.config["UPLOAD_FOLDER"]
    return sorted(os.listdir(folder)) if os.path.isdir(folder) else []


ADMIN_ROUTES = [
    ("get", "/api/admin/products"),
    ("post", "/api/admin/products"),
    ("get", "/api/admin/products/1"),
    ("put", "/api/admin/products/1"),
    ("delete", "/api/admin/products/1"),
    ("post", "/api/admin/products/1/images"),
    ("post", "/api/admin/images/1/main"),
    ("delete", "/api/admin/images/1"),
]


def call(api, method, url):
    return getattr(api, method)(url) if method in ("get", "delete") else getattr(api, method)(url, {})


@pytest.mark.parametrize(("method", "url"), ADMIN_ROUTES)
def test_guest_is_asked_to_log_in(api, method, url):
    assert call(api, method, url).status_code == 401


@pytest.mark.parametrize(("method", "url"), ADMIN_ROUTES)
def test_client_is_refused(client_api, method, url, activity_log):
    assert call(client_api, method, url).status_code == 403
    assert "access_denied" in activity_log()


def test_admin_list_shows_hidden_jars_too_a_to_z(admin_api, session):
    session.get(Product, 1).is_active = False
    session.commit()

    products = admin_api.get("/api/admin/products").get_json()["products"]

    names = [product["name"] for product in products]
    assert names == sorted(names)
    assert len(products) == session.query(Product).count()
    assert any(not product["is_active"] for product in products)


def test_admin_creates_a_jar_that_appears_in_the_shop(created, api, activity_log):
    assert created["slug"] == "dulceata-de-gutui-veche"
    assert sorted(created["ingredients"]) == ["lemon", "quinces", "sugar"]
    assert (created["price_cents"], created["stock"], created["category"]["slug"]) == (3150, 12, "preserves")
    assert created["can_delete"] is True
    assert api.get(f"/api/products/{created['slug']}").status_code == 200
    assert f"product_created | product={created['id']}" in activity_log()


def test_jar_text_is_stored_as_plain_text(admin_api):
    body = {**NEW_JAR, "name": "<b>Plum</b> Jam", "description": "<script>alert(1)</script>Thick and dark."}

    product = admin_api.post("/api/admin/products", body).get_json()["product"]

    assert product["name"] == "Plum Jam"
    assert product["description"] == "Thick and dark."


def test_a_taken_web_address_is_refused(admin_api):
    response = admin_api.post("/api/admin/products", {**NEW_JAR, "slug": "apricot-jam"})

    assert response.status_code == 409
    assert "/products/apricot-jam" in response.get_json()["error"]


def test_an_unknown_shelf_is_refused(admin_api):
    response = admin_api.post("/api/admin/products", {**NEW_JAR, "category_slug": "pickles"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Choose one of the shop's shelves."


@pytest.mark.parametrize(
    "overrides",
    [
        {"price_cents": 0},
        {"price_cents": 1_000_001},
        {"stock": -1},
        {"weight_grams": 0},
        {"name": "   "},
        {"name": "<script></script>"},
        {"description": ""},
        {"slug": "Bad Slug!"},
        {"ingredients": ["x"] * 21},
        {"surprise": True},
    ],
)
def test_jar_details_are_validated(admin_api, overrides):
    assert admin_api.post("/api/admin/products", {**NEW_JAR, **overrides}).status_code == 400


def test_admin_edits_and_hides_a_jar(admin_api, api, created, activity_log):
    body = {**NEW_JAR, "price_cents": 3400, "stock": 3, "is_active": False}

    product = admin_api.put(f"/api/admin/products/{created['id']}", body).get_json()["product"]

    assert (product["price_cents"], product["stock"], product["is_active"]) == (3400, 3, False)
    assert api.get(f"/api/products/{created['slug']}").status_code == 404
    slugs = [item["slug"] for item in api.get("/api/products?per_page=48").get_json()["items"]]
    assert created["slug"] not in slugs
    assert "changed=price_cents,stock,is_active" in activity_log()


def test_renaming_onto_another_jars_address_is_refused(admin_api, created):
    response = admin_api.put(f"/api/admin/products/{created['id']}", {**NEW_JAR, "slug": "plum-butter"})

    assert response.status_code == 409


def test_saving_a_jar_without_changes_keeps_its_own_address(admin_api, created):
    response = admin_api.put(f"/api/admin/products/{created['id']}", {**NEW_JAR, "slug": created["slug"]})

    assert response.status_code == 200


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_unknown_jar_is_404(admin_api, method):
    response = admin_api.get("/api/admin/products/9999") if method == "get" else call(admin_api, method, "/api/admin/products/9999")
    if method == "put":
        response = admin_api.put("/api/admin/products/9999", NEW_JAR)

    assert response.status_code == 404


def test_a_jar_never_ordered_is_deleted_with_its_photos(app, admin_api, created, activity_log):
    upload(admin_api, created["id"])
    assert len(upload_folder(app)) == 1

    assert admin_api.delete(f"/api/admin/products/{created['id']}").status_code == 204

    assert admin_api.get(f"/api/admin/products/{created['id']}").status_code == 404
    assert upload_folder(app) == []
    assert "product_deleted" in activity_log()


def test_a_jar_in_past_orders_cannot_be_deleted(admin_api, client_api):
    address = client_api.post(
        "/api/addresses", {"street": "Strada Lungă 5", "city": "Brașov", "county": "Brașov", "postal_code": "500035"}
    ).get_json()["address"]
    client_api.post("/api/orders", {"address_id": address["id"], "items": [{"product_id": 1, "quantity": 1}]})

    response = admin_api.delete("/api/admin/products/1")

    assert response.status_code == 409
    assert "Hide it from the shop instead" in response.get_json()["error"]
    assert admin_api.get("/api/admin/products/1").get_json()["product"]["can_delete"] is False


def test_admin_uploads_a_photo_that_the_shop_then_shows(app, admin_api, api, created, activity_log):
    response = upload(admin_api, created["id"])

    assert response.status_code == 201
    image = response.get_json()["product"]["images"][0]
    assert image["alt_text"] == "A jar of quince preserve"
    assert image["url"].startswith("/uploads/") and image["url"].endswith(".webp")
    assert upload_folder(app) == [image["url"].removeprefix("/uploads/")]
    assert api.get(f"/api/products/{created['slug']}").get_json()["product"]["image"]["url"] == image["url"]
    assert api.get(image["url"]).status_code == 200
    assert "product_image_added" in activity_log()


@pytest.mark.parametrize(
    ("data", "name", "status"),
    [
        (b"<?php system('id'); ?>", "shell.php", 400),
        (b"not really a photo", "jar.jpg", 400),
        (photo() + b"PK\x03\x04secret", "jar.jpg", 400),
    ],
)
def test_a_rejected_upload_leaves_no_photo_behind(app, admin_api, created, data, name, status):
    response = upload(admin_api, created["id"], data=data, name=name)

    assert response.status_code == status
    assert admin_api.get(f"/api/admin/products/{created['id']}").get_json()["product"]["images"] == []
    assert upload_folder(app) == []


def test_upload_over_12_mb_is_refused_with_413(app, admin_api, created):
    response = upload(admin_api, created["id"], data=b"\xff" * (13 * 1024 * 1024))

    assert response.status_code == 413
    assert upload_folder(app) == []


@pytest.mark.parametrize("alt_text", [None, "", "   ", "x" * 201])
def test_a_photo_needs_a_description_and_none_is_stored_without_one(app, admin_api, created, alt_text):
    assert upload(admin_api, created["id"], alt_text=alt_text).status_code == 400
    assert upload_folder(app) == []


def test_upload_for_an_unknown_jar_stores_nothing(app, admin_api):
    assert upload(admin_api, 9999).status_code == 404
    assert upload_folder(app) == []


def test_a_jar_has_at_most_eight_photos(admin_api, created):
    for _ in range(8):
        assert upload(admin_api, created["id"]).status_code == 201

    response = upload(admin_api, created["id"])

    assert response.status_code == 409
    assert "at most 8 photos" in response.get_json()["error"]


def test_admin_picks_the_main_photo(admin_api, api, created):
    upload(admin_api, created["id"], alt_text="First")
    second = upload(admin_api, created["id"], alt_text="Second").get_json()["product"]["images"][1]

    product = admin_api.post(f"/api/admin/images/{second['id']}/main").get_json()["product"]

    assert [image["alt_text"] for image in product["images"]] == ["Second", "First"]
    assert [image["position"] for image in product["images"]] == [0, 1]
    assert api.get(f"/api/products/{created['slug']}").get_json()["product"]["image"]["alt_text"] == "Second"


def test_admin_removes_a_photo_and_its_file(app, admin_api, created, activity_log):
    first = upload(admin_api, created["id"], alt_text="First").get_json()["product"]["images"][0]
    upload(admin_api, created["id"], alt_text="Second")

    product = admin_api.delete(f"/api/admin/images/{first['id']}").get_json()["product"]

    assert [(image["alt_text"], image["position"]) for image in product["images"]] == [("Second", 0)]
    assert first["url"].removeprefix("/uploads/") not in upload_folder(app)
    assert "product_image_removed" in activity_log()


def test_unknown_photo_is_404(admin_api):
    assert admin_api.post("/api/admin/images/9999/main").status_code == 404
    assert admin_api.delete("/api/admin/images/9999").status_code == 404
