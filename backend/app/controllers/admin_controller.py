from flask import Blueprint, jsonify, request

from app.models import RoleName
from app.schemas import AdminProductDetail, AdminProductRequest, AdminProductSummary, ImageUploadForm, parse_body, parse_form
from app.security import role_required
from app.services.admin_product_service import AdminProductService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
admin_only = role_required(RoleName.ADMIN)


def product_json(product, status: int = 200):
    return jsonify(product=AdminProductDetail.from_product(product).model_dump(mode="json")), status


@admin_bp.get("/products")
@admin_only
def list_products():
    products = AdminProductService().list_all()
    return jsonify(products=[AdminProductSummary.from_product(product).model_dump(mode="json") for product in products])


@admin_bp.post("/products")
@admin_only
def create_product():
    return product_json(AdminProductService().create(parse_body(AdminProductRequest)), 201)


@admin_bp.get("/products/<int:product_id>")
@admin_only
def get_product(product_id: int):
    return product_json(AdminProductService().get(product_id))


@admin_bp.put("/products/<int:product_id>")
@admin_only
def update_product(product_id: int):
    return product_json(AdminProductService().update(product_id, parse_body(AdminProductRequest)))


@admin_bp.delete("/products/<int:product_id>")
@admin_only
def delete_product(product_id: int):
    AdminProductService().delete(product_id)
    return "", 204


@admin_bp.post("/products/<int:product_id>/images")
@admin_only
def add_product_image(product_id: int):
    service = AdminProductService()
    return product_json(service.add_image(product_id, parse_form(ImageUploadForm), request.files.get("photo")), 201)


@admin_bp.post("/images/<int:image_id>/main")
@admin_only
def make_main_image(image_id: int):
    return product_json(AdminProductService().make_main_image(image_id))


@admin_bp.delete("/images/<int:image_id>")
@admin_only
def delete_image(image_id: int):
    return product_json(AdminProductService().delete_image(image_id))
