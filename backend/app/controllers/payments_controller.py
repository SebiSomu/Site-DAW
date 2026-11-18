from flask import Blueprint, jsonify, request

from app.extensions import csrf
from app.services.payment_service import PaymentService

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")
SIGNATURE_HEADER = "Stripe-Signature"


@payments_bp.post("/webhook")
@csrf.exempt
def payment_webhook():
    PaymentService().handle_webhook(request.get_data(), request.headers.get(SIGNATURE_HEADER))
    return jsonify(received=True)
