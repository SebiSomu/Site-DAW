from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.schemas import (
    AddressRequest,
    AddressResponse,
    CartRequest,
    CartResponse,
    OrderDetail,
    OrderRequest,
    OrderSummary,
    ReviewRequest,
    ReviewResponse,
    parse_body,
)
from app.services.activity_logger import activity_logger
from app.services.address_service import AddressService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.review_service import ReviewService

shop_bp = Blueprint("shop", __name__, url_prefix="/api")


def order_json(order):
    return jsonify(order=OrderDetail.from_order(order).model_dump(mode="json"))


@shop_bp.post("/cart/validate")
def validate_cart():
    data = parse_body(CartRequest)
    summary = CartService().price(data.items)
    activity_logger.info("cart_validated", f"lines={len(summary.lines)} total_cents={summary.total_cents}")
    return jsonify(CartResponse.from_summary(summary).model_dump(mode="json"))


@shop_bp.get("/addresses")
@login_required
def list_addresses():
    addresses = AddressService().list_for_user(current_user.id)
    return jsonify(addresses=[AddressResponse.model_validate(address).model_dump() for address in addresses])


@shop_bp.post("/addresses")
@login_required
def add_address():
    address = AddressService().add(current_user.id, parse_body(AddressRequest))
    return jsonify(address=AddressResponse.model_validate(address).model_dump()), 201


@shop_bp.delete("/addresses/<int:address_id>")
@login_required
def archive_address(address_id: int):
    AddressService().archive(address_id, current_user.id)
    return "", 204


@shop_bp.post("/orders")
@login_required
def place_order():
    return order_json(OrderService().place(current_user.id, parse_body(OrderRequest))), 201


@shop_bp.get("/orders")
@login_required
def list_orders():
    orders = OrderService().list_for_user(current_user.id)
    return jsonify(orders=[OrderSummary.from_order(order).model_dump(mode="json") for order in orders])


@shop_bp.get("/orders/<int:order_id>")
@login_required
def get_order(order_id: int):
    return order_json(OrderService().get_for_user(order_id, current_user.id))


@shop_bp.post("/orders/<int:order_id>/cancel")
@login_required
def cancel_order(order_id: int):
    return order_json(OrderService().cancel(order_id, current_user.id))


@shop_bp.get("/products/<int:product_id>/reviews/eligibility")
@login_required
def review_eligibility(product_id: int):
    return jsonify(can_review=ReviewService().can_review(current_user.id, product_id))


@shop_bp.post("/products/<int:product_id>/reviews")
@login_required
def add_review(product_id: int):
    review = ReviewService().add(current_user.id, product_id, parse_body(ReviewRequest))
    return jsonify(review=ReviewResponse.from_review(review).model_dump(mode="json")), 201
