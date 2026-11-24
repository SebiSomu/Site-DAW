from functools import wraps

from flask import request

from app.errors import CaptchaError
from app.services.activity_logger import activity_logger
from app.services.captcha import get_captcha_verifier

CAPTCHA_HEADER = "X-Captcha-Token"
MAX_TOKEN_LENGTH = 2048


def read_token() -> str:
    return request.headers.get(CAPTCHA_HEADER, "").strip()


def reject(reason: str) -> None:
    activity_logger.warning("captcha_failed", f"route={request.path} reason={reason}")
    raise CaptchaError()


def captcha_required(view):
    @wraps(view)
    def checked(*args, **kwargs):
        token = read_token()
        if not token:
            reject("missing")
        if len(token) > MAX_TOKEN_LENGTH:
            reject("too_long")
        result = get_captcha_verifier().verify(token, request.remote_addr)
        if not result.success:
            reject(",".join(result.error_codes) or "invalid")
        return view(*args, **kwargs)

    return checked
