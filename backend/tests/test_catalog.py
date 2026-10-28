import pytest

from app.models import Review
from app.repositories import ProductRepository, UserRepository
from app.seed import DEMO_CLIENT_EMAIL
from app.seed.data import CATEGORIES, PRODUCTS


def test_categories_lists_every_seeded_category(api):
    response = api.get("/api/categories")

    assert response.status_code == 200
    assert [category["slug"] for category in response.get_json()["categories"]] == [seed.slug for seed in CATEGORIES]


def test_products_are_paginated(api):
    body = api.get("/api/products?per_page=5&page=3").get_json()

    assert body["total"] == len(PRODUCTS)
    assert body["pages"] == 3
    assert body["page"] == 3
    assert len(body["items"]) == len(PRODUCTS) - 10


def test_products_filter_by_category(api):
    items = api.get("/api/products?category=preserves").get_json()["items"]

    expected = {seed.slug for seed in PRODUCTS if seed.category_slug == "preserves"}
    assert {item["slug"] for item in items} == expected
    assert all(item["category"]["slug"] == "preserves" for item in items)


def test_products_search_matches_name_and_description(api):
    slugs = {item["slug"] for item in api.get("/api/products?q=walnut").get_json()["items"]}

    assert {"green-walnut-preserve", "fig-and-walnut-jam"} <= slugs
    assert "strawberry-jam" not in slugs


@pytest.mark.parametrize(("sort", "reverse"), [("price-asc", False), ("price-desc", True)])
def test_products_sort_by_price(api, sort, reverse):
    prices = [item["price_bani"] for item in api.get(f"/api/products?sort={sort}&per_page=48").get_json()["items"]]

    assert prices == sorted(prices, reverse=reverse)


@pytest.mark.parametrize(("query", "field"), [("sort=cheapest", "sort"), ("per_page=500", "per_page"), ("page=0", "page")])
def test_products_reject_invalid_query(api, query, field):
    response = api.get(f"/api/products?{query}")

    assert response.status_code == 400
    assert response.get_json()["error"].startswith(f"{field}:")


def test_products_search_is_safe_against_sql_injection(api):
    response = api.get("/api/products?q=' OR 1=1 --")

    assert response.status_code == 200
    assert response.get_json()["total"] == 0


def test_inactive_products_are_hidden(api, session):
    ProductRepository().get_by_slug("apricot-jam").is_active = False
    session.commit()

    slugs = {item["slug"] for item in api.get("/api/products?per_page=48").get_json()["items"]}
    assert "apricot-jam" not in slugs
    assert api.get("/api/products/apricot-jam").status_code == 404


def test_product_detail_includes_ingredients_and_reviews(api, session):
    product = ProductRepository().get_by_slug("apricot-jam")
    session.add(Review(user=UserRepository().get_by_email(DEMO_CLIENT_EMAIL), product=product, rating=4, comment="Lovely."))
    session.commit()

    response = api.get("/api/products/apricot-jam")

    assert response.status_code == 200
    detail = response.get_json()["product"]
    assert detail["price_bani"] == 2450
    assert detail["category"] == {"name": "Jams", "slug": "jams"}
    assert detail["ingredients"] == ["apricots", "sugar", "lemon"]
    assert detail["average_rating"] == 4.0
    assert detail["reviews"][0]["author"] == "Andrei I."
    assert "user_id" not in detail["reviews"][0]


def test_unknown_product_returns_json_404(api):
    response = api.get("/api/products/no-such-jar")

    assert response.status_code == 404
    assert "could not find this jar" in response.get_json()["error"]


def test_robots_points_to_sitemap(api):
    body = api.get("/robots.txt").get_data(as_text=True)

    assert "Sitemap: http://localhost/sitemap.xml" in body
    assert "Disallow: /admin" in body


def test_sitemap_lists_categories_and_products(api):
    response = api.get("/sitemap.xml")

    assert response.mimetype == "application/xml"
    body = response.get_data(as_text=True)
    assert "<loc>http://localhost/products?category=jams</loc>" in body
    assert body.count("<loc>http://localhost/products/") == len(PRODUCTS)
