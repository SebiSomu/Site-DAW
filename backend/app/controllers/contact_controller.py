from flask import Blueprint, jsonify

from app.schemas import parse_body
from app.schemas.contact import ContactRequest
from app.services.contact_service import ContactService

contact_bp = Blueprint("contact", __name__, url_prefix="/api")


@contact_bp.post("/contact")
def send_message():
    ContactService().send(parse_body(ContactRequest))
    return jsonify(sent=True), 201
