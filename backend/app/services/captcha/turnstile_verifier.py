import json
import logging
from typing import Callable
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.errors import CaptchaUnavailableError
from app.services.captcha.verifier import CaptchaResult, CaptchaVerifier

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TIMEOUT_SECONDS = 5
CONFIGURATION_ERRORS = frozenset({"missing-input-secret", "invalid-input-secret", "internal-error"})

logger = logging.getLogger(__name__)

Transport = Callable[[Request, float], bytes]


def send_request(http_request: Request, timeout: float) -> bytes:
    with urlopen(http_request, timeout=timeout) as response:
        return response.read()


class TurnstileVerifier(CaptchaVerifier):
    def __init__(self, site_key: str, secret_key: str, transport: Transport = send_request) -> None:
        self._site_key = site_key
        self._secret_key = secret_key
        self._transport = transport

    @property
    def site_key(self) -> str:
        return self._site_key

    def verify(self, token: str, remote_ip: str | None) -> CaptchaResult:
        fields = {"secret": self._secret_key, "response": token}
        if remote_ip:
            fields["remoteip"] = remote_ip
        http_request = Request(
            SITEVERIFY_URL,
            data=urlencode(fields).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        body = self._call(http_request)
        error_codes = tuple(str(code) for code in body.get("error-codes", []))
        if CONFIGURATION_ERRORS.intersection(error_codes):
            logger.error("Turnstile rejected our configuration: %s", ", ".join(error_codes))
            raise CaptchaUnavailableError()
        return CaptchaResult(success=body.get("success") is True, error_codes=error_codes)

    def _call(self, http_request: Request) -> dict:
        try:
            raw = self._transport(http_request, TIMEOUT_SECONDS)
            body = json.loads(raw)
        except (URLError, TimeoutError, OSError, ValueError) as error:
            logger.warning("Turnstile could not be reached: %s", type(error).__name__)
            raise CaptchaUnavailableError() from error
        if not isinstance(body, dict):
            raise CaptchaUnavailableError()
        return body
