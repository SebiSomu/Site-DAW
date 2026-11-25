import json

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import create_app
from app.extensions import db
from app.rate_limits import FALLBACK_WAIT_SECONDS, describe_wait, seconds_until_reset
from app.services.captcha import TurnstileVerifier


@pytest.fixture()
def failing_app(tmp_path):
    application = create_app(
        "testing", {"ACTIVITY_LOG_PATH": str(tmp_path / "activity.log"), "PROPAGATE_EXCEPTIONS": False}
    )

    def crash():
        raise RuntimeError("database password is hunter2")

    def duplicate():
        raise IntegrityError("INSERT INTO users", {}, Exception("UNIQUE constraint failed: users.email"))

    application.add_url_rule("/api/test/crash", "crash", crash)
    application.add_url_rule("/api/test/duplicate", "duplicate", duplicate)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


def test_unexpected_error_is_a_generic_500_without_details(failing_app):
    response = failing_app.test_client().get("/api/test/crash")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Something went wrong. Please try again later."}
    assert b"hunter2" not in response.data
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_database_conflict_is_a_409_without_sql(failing_app):
    response = failing_app.test_client().get("/api/test/duplicate")

    assert response.status_code == 409
    assert response.get_json() == {"error": "This conflicts with existing data."}
    assert b"UNIQUE" not in response.data


def test_unknown_route_and_wrong_method_are_json(api):
    missing = api.get("/api/nothing-here")
    wrong_method = api.get("/api/auth/login")

    assert missing.status_code == 404 and "error" in missing.get_json()
    assert wrong_method.status_code == 405 and "error" in wrong_method.get_json()


def test_health_reports_an_unavailable_database_as_503(api, monkeypatch):
    def broken(*args, **kwargs):
        raise SQLAlchemyError("disk I/O error")

    monkeypatch.setattr(db.session, "execute", broken)

    response = api.get("/api/health")

    assert response.status_code == 503
    assert response.get_json() == {"status": "error", "database": "unavailable"}


def test_seed_command_creates_the_shop_and_the_demo_client(app):
    result = app.test_cli_runner().invoke(args=["seed", "--demo"])

    assert result.exit_code == 0
    assert "Seed complete" in result.output
    assert "Demo client:" in result.output
    assert "ADMIN_PASSWORD is not set" not in result.output


def test_seed_command_says_when_no_admin_was_created(app):
    app.config["ADMIN_PASSWORD"] = ""

    result = app.test_cli_runner().invoke(args=["seed"])

    assert result.exit_code == 0
    assert "ADMIN_PASSWORD is not set in .env" in result.output
    assert "Demo client:" not in result.output


def test_wait_time_falls_back_to_a_minute_without_a_current_limit(app):
    with app.test_request_context("/api/health"):
        assert seconds_until_reset() == FALLBACK_WAIT_SECONDS


@pytest.mark.parametrize(("seconds", "words"), [(1, "1 second"), (2, "2 seconds"), (60, "60 seconds")])
def test_wait_time_is_worded(seconds, words):
    assert describe_wait(seconds) == words


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def read(self) -> bytes:
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        return None


def test_turnstile_default_transport_posts_with_a_timeout(monkeypatch):
    calls = []

    def fake_urlopen(http_request, timeout):
        calls.append((http_request.full_url, timeout))
        return FakeResponse(json.dumps({"success": True}).encode())

    monkeypatch.setattr("app.services.captcha.turnstile_verifier.urlopen", fake_urlopen)

    result = TurnstileVerifier("site", "secret").verify("token", "203.0.113.9")

    assert result.success
    assert calls == [("https://challenges.cloudflare.com/turnstile/v0/siteverify", 5)]
