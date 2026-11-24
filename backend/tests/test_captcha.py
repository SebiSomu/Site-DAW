import json
from urllib.error import URLError
from urllib.parse import parse_qs

import pytest

from app.errors import CaptchaUnavailableError
from app.security import CAPTCHA_HEADER
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD
from app.services.captcha import FAKE_CAPTCHA_TOKEN, FAKE_SITE_KEY, TurnstileVerifier, build_verifier
from app.services.captcha.turnstile_verifier import SITEVERIFY_URL

PROTECTED = {
    "/api/auth/login": {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD},
    "/api/auth/register": {
        "email": "new.client@example.com",
        "password": "Long-enough-123",
        "first_name": "Ana",
        "last_name": "Pop",
    },
    "/api/contact": {
        "name": "Ana Pop",
        "email": "ana@example.com",
        "subject": "A wedding order",
        "message": "Could you make forty small jars?",
    },
}
SUCCESS_STATUS = {"/api/auth/login": 200, "/api/auth/register": 201, "/api/contact": 201}


def post_with_token(api, route: str, token: str | None):
    headers = {"X-CSRFToken": api.csrf_token}
    if token is not None:
        headers[CAPTCHA_HEADER] = token
    with api.client.application.app_context():
        return api.client.post(route, json=PROTECTED[route], headers=headers)


@pytest.mark.parametrize("route", PROTECTED)
def test_missing_token_is_rejected_and_logged(api, activity_log, route):
    response = post_with_token(api, route, None)

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please complete the security check and try again."
    assert f"captcha_failed | route={route} reason=missing" in activity_log()


@pytest.mark.parametrize("route", PROTECTED)
def test_invalid_token_is_rejected(api, activity_log, route):
    response = post_with_token(api, route, "forged-token")

    assert response.status_code == 400
    assert "reason=invalid-input-response" in activity_log()


@pytest.mark.parametrize("route", PROTECTED)
def test_valid_token_is_accepted(api, route):
    assert post_with_token(api, route, FAKE_CAPTCHA_TOKEN).status_code == SUCCESS_STATUS[route]


def test_overlong_token_is_rejected_without_calling_the_verifier(app, api, activity_log):
    response = post_with_token(api, "/api/contact", "x" * 2049)

    assert response.status_code == 400
    assert "reason=too_long" in activity_log()
    assert app.extensions["captcha_verifier"].calls == []


def test_verifier_receives_the_client_ip(app, api):
    post_with_token(api, "/api/contact", FAKE_CAPTCHA_TOKEN)

    assert app.extensions["captcha_verifier"].calls == [(FAKE_CAPTCHA_TOKEN, "127.0.0.1")]


def test_rejected_captcha_creates_nothing(api):
    post_with_token(api, "/api/auth/register", "forged-token")

    assert post_with_token(api, "/api/auth/register", FAKE_CAPTCHA_TOKEN).status_code == 201


def test_unreachable_verifier_is_503_and_never_lets_the_request_through(app, api, monkeypatch):
    def unavailable(token, remote_ip):
        raise CaptchaUnavailableError()

    monkeypatch.setattr(app.extensions["captcha_verifier"], "verify", unavailable)

    response = post_with_token(api, "/api/auth/login", FAKE_CAPTCHA_TOKEN)

    assert response.status_code == 503
    assert api.get("/api/auth/me").status_code == 401


def test_csrf_is_still_checked_before_the_captcha(app, seeded):
    response = app.test_client().post(
        "/api/contact", json=PROTECTED["/api/contact"], headers={CAPTCHA_HEADER: FAKE_CAPTCHA_TOKEN}
    )

    assert response.status_code == 400
    assert "security token" in response.get_json()["error"]


def test_site_key_endpoint(api):
    assert api.get("/api/captcha").get_json() == {"site_key": FAKE_SITE_KEY}


def test_config_selects_the_verifier():
    assert isinstance(
        build_verifier({"CAPTCHA_VERIFIER": "turnstile", "TURNSTILE_SITE_KEY": "s", "TURNSTILE_SECRET_KEY": "k"}),
        TurnstileVerifier,
    )
    with pytest.raises(ValueError):
        build_verifier({"CAPTCHA_VERIFIER": "unknown"})


class RecordingTransport:
    def __init__(self, reply) -> None:
        self.reply = reply
        self.requests = []

    def __call__(self, http_request, timeout):
        self.requests.append((http_request, timeout))
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def test_turnstile_sends_secret_token_and_ip():
    transport = RecordingTransport(json.dumps({"success": True}).encode())
    verifier = TurnstileVerifier("site", "secret", transport)

    result = verifier.verify("token-1", "203.0.113.9")

    http_request, timeout = transport.requests[0]
    assert result.success
    assert http_request.full_url == SITEVERIFY_URL
    assert http_request.get_method() == "POST"
    assert parse_qs(http_request.data.decode()) == {
        "secret": ["secret"],
        "response": ["token-1"],
        "remoteip": ["203.0.113.9"],
    }
    assert timeout <= 5


def test_turnstile_failure_keeps_error_codes():
    reply = json.dumps({"success": False, "error-codes": ["timeout-or-duplicate"]}).encode()

    result = TurnstileVerifier("site", "secret", RecordingTransport(reply)).verify("used", None)

    assert not result.success
    assert result.error_codes == ("timeout-or-duplicate",)


@pytest.mark.parametrize(
    "reply",
    [
        URLError("down"),
        TimeoutError(),
        b"<html>not json</html>",
        b"[]",
        json.dumps({"success": False, "error-codes": ["invalid-input-secret"]}).encode(),
    ],
)
def test_turnstile_outage_or_bad_secret_is_unavailable(reply):
    with pytest.raises(CaptchaUnavailableError):
        TurnstileVerifier("site", "secret", RecordingTransport(reply)).verify("token", None)
