import pytest

from app.models import RoleName
from app.repositories import UserRepository
from app.security import role_required
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD

NEW_CLIENT = {
    "email": "Ana.Pop@Example.com",
    "password": "jam-lover-2026",
    "first_name": "Ana",
    "last_name": "Pop",
    "phone": "+40712345678",
}


@pytest.fixture()
def admin_only_route(app):
    @app.get("/api/test/admin-only")
    @role_required(RoleName.ADMIN)
    def admin_only():
        return {"ok": True}


def test_register_creates_logged_in_client_with_hashed_password(api):
    response = api.post("/api/auth/register", NEW_CLIENT)

    assert response.status_code == 201
    user = response.get_json()["user"]
    assert user["email"] == "ana.pop@example.com"
    assert user["role"] == RoleName.CLIENT.value
    assert "password" not in user and "password_hash" not in user
    assert api.get("/api/auth/me").get_json()["user"]["id"] == user["id"]
    stored = UserRepository().get_by_email(NEW_CLIENT["email"])
    assert stored.password_hash.startswith("scrypt:")


def test_register_rejects_duplicate_email_case_insensitively(api):
    response = api.post("/api/auth/register", {**NEW_CLIENT, "email": DEMO_CLIENT_EMAIL.upper()})

    assert response.status_code == 409
    assert response.get_json()["error"] == "An account with this email already exists."


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        ({"password": "short"}, "password"),
        ({"email": "not-an-email"}, "email"),
        ({"first_name": "   "}, "first_name"),
        ({"phone": "call me"}, "phone"),
        ({"role": "admin"}, "role"),
    ],
)
def test_register_validates_input(api, overrides, field):
    response = api.post("/api/auth/register", {**NEW_CLIENT, **overrides})

    assert response.status_code == 400
    assert response.get_json()["error"].startswith(f"{field}:")


def test_login_with_wrong_password_is_rejected_and_logged(api, activity_log):
    response = api.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": "wrong-password"})

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email or password."
    assert f"| WARNING | 127.0.0.1 | - | login_failed | email={DEMO_CLIENT_EMAIL}" in activity_log()


def test_login_starts_session_and_is_logged(api, activity_log):
    response = api.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD})

    assert response.status_code == 200
    user_id = response.get_json()["user"]["id"]
    assert api.get("/api/auth/me").status_code == 200
    assert f"| INFO | 127.0.0.1 | {user_id} | login | email={DEMO_CLIENT_EMAIL}" in activity_log()


def test_logout_ends_session(api, activity_log):
    api.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD})

    assert api.post("/api/auth/logout").status_code == 204
    assert api.get("/api/auth/me").status_code == 401
    assert "| logout |" in activity_log()


def test_guest_gets_json_401(api):
    response = api.get("/api/auth/me")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Please log in to continue."}


def test_post_without_csrf_token_is_rejected(app, seeded, activity_log):
    response = app.test_client().post(
        "/api/auth/login", json={"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD}
    )

    assert response.status_code == 400
    assert "security token" in response.get_json()["error"]
    assert "csrf_rejected" in activity_log()


@pytest.mark.parametrize(
    ("credentials", "expected_status"),
    [
        (None, 401),
        ((DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD), 403),
        (("admin@example.com", "Test-Password-123"), 200),
    ],
)
def test_role_required_enforces_admin_role(admin_only_route, api, credentials, expected_status):
    if credentials:
        email, password = credentials
        assert api.post("/api/auth/login", {"email": email, "password": password}).status_code == 200

    assert api.get("/api/test/admin-only").status_code == expected_status


def test_unknown_api_route_returns_json_404(api):
    response = api.get("/api/does-not-exist")

    assert response.status_code == 404
    assert "error" in response.get_json()
