from flask import Blueprint, current_app, jsonify, request

from app.models import RoleName
from app.schemas import (
    AdminOrderDetail,
    AdminOrderQuery,
    AdminOrderSummary,
    AdminProductDetail,
    AdminProductRequest,
    AdminProductSummary,
    ImageUploadForm,
    OrderStatusChangeRequest,
    parse_body,
    parse_form,
    parse_query,
)
from app.schemas.contact import (
    ContactMessageResponse,
    LogEntryResponse,
    LogPageResponse,
    LogQuery,
    MessagesPageResponse,
    PageQuery,
    page_count,
)
from app.security import role_required
from app.services.activity_log_reader import ActivityLogReader, LogFilter
from app.services.admin_order_service import AdminOrderService
from app.services.admin_product_service import AdminProductService
from app.services.contact_service import ContactService

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


def admin_order_json(service: AdminOrderService, order):
    return jsonify(order=AdminOrderDetail.from_order(order, service.next_statuses(order)).model_dump(mode="json"))


@admin_bp.get("/summary")
@admin_only
def summary():
    return jsonify(AdminOrderService().summary().model_dump(mode="json"))


@admin_bp.get("/orders")
@admin_only
def list_orders():
    query = parse_query(AdminOrderQuery)
    orders = AdminOrderService().list_orders(query.status)
    return jsonify(orders=[AdminOrderSummary.from_order(order).model_dump(mode="json") for order in orders])


@admin_bp.get("/orders/<int:order_id>")
@admin_only
def get_order(order_id: int):
    service = AdminOrderService()
    return admin_order_json(service, service.get(order_id))


@admin_bp.patch("/orders/<int:order_id>/status")
@admin_only
def change_order_status(order_id: int):
    service = AdminOrderService()
    return admin_order_json(service, service.change_status(order_id, parse_body(OrderStatusChangeRequest).status))


@admin_bp.get("/messages")
@admin_only
def list_messages():
    query = parse_query(PageQuery)
    messages, total = ContactService().page(query.page, query.per_page)
    response = MessagesPageResponse(
        messages=[ContactMessageResponse.from_message(message) for message in messages],
        total=total,
        page=query.page,
        per_page=query.per_page,
        pages=page_count(total, query.per_page),
    )
    return jsonify(response.model_dump(mode="json"))


@admin_bp.delete("/messages/<int:message_id>")
@admin_only
def delete_message(message_id: int):
    ContactService().delete(message_id)
    return "", 204


@admin_bp.get("/logs")
@admin_only
def activity_log():
    query = parse_query(LogQuery)
    log_filter = LogFilter(
        user_id=query.user_id,
        action=query.action,
        level=query.level,
        date_from=query.date_from,
        date_to=query.date_to,
    )
    found = ActivityLogReader(current_app.config["ACTIVITY_LOG_PATH"]).search(log_filter, query.page, query.per_page)
    response = LogPageResponse(
        entries=[LogEntryResponse(**vars(entry)) for entry in found.entries],
        total=found.total,
        page=found.page,
        per_page=found.per_page,
        pages=page_count(found.total, found.per_page),
        actions=found.actions,
    )
    return jsonify(response.model_dump(mode="json"))
