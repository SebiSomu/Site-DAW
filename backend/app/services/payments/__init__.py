from typing import Mapping

from flask import Flask, current_app

from app.services.payments.fake_gateway import FAKE_SIGNATURE, FakeGateway
from app.services.payments.gateway import (
    CheckoutSession,
    CheckoutStatus,
    PaymentEvent,
    PaymentEventKind,
    PaymentGateway,
)
from app.services.payments.stripe_gateway import StripeGateway

GATEWAY_EXTENSION = "payment_gateway"


def build_gateway(config: Mapping) -> PaymentGateway:
    name = config["PAYMENT_GATEWAY"]
    if name == "stripe":
        return StripeGateway(config["STRIPE_SECRET_KEY"], config["STRIPE_WEBHOOK_SECRET"], config["SITE_URL"])
    if name == "fake":
        return FakeGateway(config["SITE_URL"])
    raise ValueError(f"Unknown payment gateway: {name}")


def init_payments(app: Flask) -> None:
    app.extensions[GATEWAY_EXTENSION] = build_gateway(app.config)


def get_payment_gateway() -> PaymentGateway:
    return current_app.extensions[GATEWAY_EXTENSION]


__all__ = [
    "CheckoutSession",
    "CheckoutStatus",
    "FAKE_SIGNATURE",
    "FakeGateway",
    "PaymentEvent",
    "PaymentEventKind",
    "PaymentGateway",
    "StripeGateway",
    "build_gateway",
    "get_payment_gateway",
    "init_payments",
]
