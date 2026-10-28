from flask import Blueprint, jsonify

from app.schemas import CategoryResponse, ProductDetail, ProductPageResponse, ProductQuery, parse_query
from app.services.catalog_service import CatalogService

catalog_bp = Blueprint("catalog", __name__, url_prefix="/api")


@catalog_bp.get("/categories")
def categories():
    items = CatalogService().list_categories()
    return jsonify(categories=[CategoryResponse.model_validate(category).model_dump() for category in items])


@catalog_bp.get("/products")
def products():
    page = CatalogService().search_products(parse_query(ProductQuery))
    return jsonify(ProductPageResponse.from_page(page).model_dump(mode="json"))


@catalog_bp.get("/products/<slug>")
def product(slug: str):
    return jsonify(product=ProductDetail.from_product(CatalogService().get_product(slug)).model_dump(mode="json"))
