from typing import Mapping

from flask import Flask, current_app

from app.services.captcha.fake_verifier import FAKE_CAPTCHA_TOKEN, FAKE_SITE_KEY, FakeVerifier
from app.services.captcha.turnstile_verifier import TurnstileVerifier
from app.services.captcha.verifier import CaptchaResult, CaptchaVerifier

VERIFIER_EXTENSION = "captcha_verifier"


def build_verifier(config: Mapping) -> CaptchaVerifier:
    name = config["CAPTCHA_VERIFIER"]
    if name == "turnstile":
        return TurnstileVerifier(config["TURNSTILE_SITE_KEY"], config["TURNSTILE_SECRET_KEY"])
    if name == "fake":
        return FakeVerifier()
    raise ValueError(f"Unknown CAPTCHA verifier: {name}")


def init_captcha(app: Flask) -> None:
    app.extensions[VERIFIER_EXTENSION] = build_verifier(app.config)


def get_captcha_verifier() -> CaptchaVerifier:
    return current_app.extensions[VERIFIER_EXTENSION]


__all__ = [
    "FAKE_CAPTCHA_TOKEN",
    "FAKE_SITE_KEY",
    "CaptchaResult",
    "CaptchaVerifier",
    "FakeVerifier",
    "TurnstileVerifier",
    "build_verifier",
    "get_captcha_verifier",
    "init_captcha",
]
