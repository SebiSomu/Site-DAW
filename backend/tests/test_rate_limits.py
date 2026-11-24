import pytest

from app import create_app
from app.extensions import db as database
from app.extensions import limiter
from app.seed import DatabaseSeeder
from tests.conftest import ApiClient

STRICT_ROUTES = ["/api/auth/login", "/api/auth/register", "/api/contact"]


@pytest.fixture()
def limited_app(tmp_path):
    application = create_app(
        "testing",
        {
            "ACTIVITY_LOG_PATH": str(tmp_path / "activity.log"),
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
            "RATELIMIT_ENABLED": True,
        },
    )
    with application.app_context():
        database.create_all()
        DatabaseSeeder().run(include_demo_client=True)
        yield application
        database.session.remove()
        database.drop_all()
    limiter.enabled = False


def read_log(app) -> str:
    with open(app.config["ACTIVITY_LOG_PATH"], encoding="utf-8") as log_file:
        return log_file.read()


def test_101st_request_in_a_minute_is_429_with_retry_after(limited_app):
    client = limited_app.test_client()
    statuses = [client.get("/api/health").status_code for _ in range(100)]

    response = client.get("/api/health")

    assert set(statuses) == {200}
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60
    assert response.get_json()["error"].startswith("Too many requests. Please try again in ")
    assert "rate_limited" in read_log(limited_app)
    assert "route=GET /api/health" in read_log(limited_app)


def test_limit_is_counted_per_ip(limited_app):
    client = limited_app.test_client()
    for _ in range(100):
        client.get("/api/health")

    other = client.get("/api/health", environ_base={"REMOTE_ADDR": "203.0.113.9"})

    assert client.get("/api/health").status_code == 429
    assert other.status_code == 200


@pytest.mark.parametrize("route", STRICT_ROUTES)
def test_sixth_attempt_on_a_strict_route_is_429(limited_app, route):
    api = ApiClient(limited_app.test_client())
    statuses = [api.post(route, json={}).status_code for _ in range(5)]

    response = api.post(route, json={})

    assert 429 not in statuses
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert api.get("/api/health").status_code == 200


def test_strict_route_attempts_also_count_toward_the_global_limit(limited_app):
    api = ApiClient(limited_app.test_client())
    for _ in range(5):
        api.post("/api/auth/login", json={})
    statuses = [api.get("/api/health").status_code for _ in range(94)]

    assert set(statuses) == {200}
    assert api.get("/api/health").status_code == 429


def test_stripe_webhook_is_never_limited(limited_app):
    client = limited_app.test_client()
    statuses = {client.post("/api/payments/webhook", data=b"{}").status_code for _ in range(110)}

    assert 429 not in statuses


def test_limits_are_off_in_the_default_testing_config(api):
    statuses = {api.post("/api/auth/login", json={}).status_code for _ in range(8)}

    assert 429 not in statuses
