from datetime import date, timedelta

import pytest

from app.models import ContactMessage
from app.seed import DEMO_CLIENT_EMAIL, DEMO_CLIENT_PASSWORD
from app.services.activity_log_reader import parse_line

MESSAGE = {
    "name": "Ana Pop",
    "email": "Ana.Pop@Example.com",
    "subject": "Plum butter for a wedding",
    "message": "Could Mum make 40 small jars for June?",
}


@pytest.fixture()
def admin_api(new_api):
    admin = new_api()
    assert admin.post("/api/auth/login", {"email": "admin@example.com", "password": "Test-Password-123"}).status_code == 200
    return admin


@pytest.fixture()
def client_api(new_api):
    client = new_api()
    assert client.post("/api/auth/login", {"email": DEMO_CLIENT_EMAIL, "password": DEMO_CLIENT_PASSWORD}).status_code == 200
    return client


def write_log(app, lines, suffix=""):
    with open(app.config["ACTIVITY_LOG_PATH"] + suffix, "a", encoding="utf-8") as log_file:
        log_file.write("\n".join(lines) + "\n")


def test_a_guest_sends_a_message_that_is_stored(api, session, activity_log):
    response = api.post("/api/contact", MESSAGE)

    assert response.status_code == 201
    stored = session.query(ContactMessage).one()
    assert (stored.name, stored.email, stored.subject) == ("Ana Pop", "ana.pop@example.com", MESSAGE["subject"])
    assert f"contact_message | message={stored.id}" in activity_log()
    assert "ana.pop@example.com" not in activity_log()


def test_message_text_is_stored_as_plain_text(api, session):
    api.post("/api/contact", {**MESSAGE, "subject": "<b>Hi</b>", "message": "<script>alert(1)</script>Hello Mum"})

    stored = session.query(ContactMessage).one()
    assert (stored.subject, stored.message) == ("Hi", "Hello Mum")


@pytest.mark.parametrize(
    "overrides",
    [
        {"email": "not-an-email"},
        {"name": " "},
        {"subject": ""},
        {"message": ""},
        {"message": "x" * 5001},
        {"message": "<script></script>"},
        {"website": "spam.example"},
    ],
)
def test_contact_form_is_validated(api, session, overrides):
    assert api.post("/api/contact", {**MESSAGE, **overrides}).status_code == 400
    assert session.query(ContactMessage).count() == 0


def test_contact_form_needs_the_csrf_token(app, seeded):
    response = app.test_client().post("/api/contact", json=MESSAGE)

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("method", "url"), [("get", "/api/admin/messages"), ("delete", "/api/admin/messages/1"), ("get", "/api/admin/logs")]
)
def test_messages_and_logs_are_for_the_admin_only(new_api, client_api, method, url):
    assert getattr(new_api(), method)(url).status_code == 401
    assert getattr(client_api, method)(url).status_code == 403


def test_admin_reads_messages_newest_first_a_page_at_a_time(api, admin_api):
    for number in range(3):
        api.post("/api/contact", {**MESSAGE, "subject": f"Question {number}"})

    first = admin_api.get("/api/admin/messages?per_page=2").get_json()
    second = admin_api.get("/api/admin/messages?per_page=2&page=2").get_json()

    assert [message["subject"] for message in first["messages"]] == ["Question 2", "Question 1"]
    assert [message["subject"] for message in second["messages"]] == ["Question 0"]
    assert (first["total"], first["pages"]) == (3, 2)
    assert admin_api.get("/api/admin/messages?per_page=500").status_code == 400


def test_admin_deletes_a_message(api, admin_api, session, activity_log):
    api.post("/api/contact", MESSAGE)
    message_id = session.query(ContactMessage).one().id

    assert admin_api.delete(f"/api/admin/messages/{message_id}").status_code == 204
    assert admin_api.get("/api/admin/messages").get_json()["total"] == 0
    assert f"message_deleted | message={message_id}" in activity_log()
    assert admin_api.delete(f"/api/admin/messages/{message_id}").status_code == 404


def test_log_viewer_shows_real_activity_newest_first(admin_api, client_api):
    entries = admin_api.get("/api/admin/logs").get_json()["entries"]

    assert (entries[0]["action"], entries[0]["user_id"]) == ("login", 2)
    assert any(entry["action"] == "login" and entry["user_id"] == 1 for entry in entries)
    assert entries == sorted(entries, key=lambda entry: entry["timestamp"], reverse=True)


def test_log_viewer_filters_by_action_user_and_level(admin_api, new_api):
    guest = new_api()
    guest.post("/api/auth/login", {"email": "nobody@example.com", "password": "wrong-password"})

    failed = admin_api.get("/api/admin/logs?action=login_failed").get_json()
    warnings = admin_api.get("/api/admin/logs?level=WARNING").get_json()
    admin_only = admin_api.get("/api/admin/logs?user_id=1").get_json()

    assert failed["total"] == 1 and failed["entries"][0]["user_id"] is None
    assert all(entry["level"] == "WARNING" for entry in warnings["entries"]) and warnings["total"] >= 1
    assert all(entry["user_id"] == 1 for entry in admin_only["entries"])
    assert {"login", "login_failed"} <= set(failed["actions"])


def test_log_viewer_filters_by_date(admin_api):
    today = date.today()
    yesterday = today - timedelta(days=1)

    assert admin_api.get(f"/api/admin/logs?date_from={today}&date_to={today}").get_json()["total"] >= 1
    assert admin_api.get(f"/api/admin/logs?date_to={yesterday}").get_json()["total"] == 0


def test_log_viewer_reads_rotated_files_after_the_current_one(app, admin_api):
    write_log(app, ["2026-01-02 09:00:00,000 | INFO | 10.0.0.1 | 7 | old_action | from=the first rotated file"], ".1")
    write_log(app, ["2025-12-31 23:59:00,000 | INFO | 10.0.0.1 | 7 | oldest_action | from=the second"], ".2")

    entries = admin_api.get("/api/admin/logs?per_page=200").get_json()["entries"]

    assert [entry["action"] for entry in entries[-2:]] == ["old_action", "oldest_action"]


def test_log_viewer_skips_lines_it_cannot_read_and_keeps_pipes_in_details(app, admin_api):
    write_log(
        app,
        [
            "Traceback (most recent call last):",
            "2026-13-45 99:99:99,000 | INFO | - | - | broken_date | x",
            "2026-11-18 12:00:00,000 | WARNING | 10.0.0.2 | - | csrf_rejected | The CSRF token | is missing.",
        ],
    )

    entries = admin_api.get("/api/admin/logs?action=csrf_rejected").get_json()["entries"]

    assert entries[0]["details"] == "The CSRF token | is missing."
    assert admin_api.get("/api/admin/logs?action=broken_date").get_json()["total"] == 0


def test_log_viewer_pages_through_entries(app, admin_api):
    write_log(app, [f"2026-11-18 10:00:{second:02d},000 | INFO | - | - | bulk_action | n={second}" for second in range(5)])

    page = admin_api.get("/api/admin/logs?action=bulk_action&per_page=2&page=3").get_json()

    assert (page["total"], page["pages"], len(page["entries"])) == (5, 3, 1)
    assert page["entries"][0]["details"] == "n=0"


@pytest.mark.parametrize(
    "query",
    [
        "action=DROP TABLE users",
        "level=DEBUG",
        "user_id=abc",
        "date_from=2026-11-18&date_to=2026-11-01",
        "per_page=1000",
        "surprise=1",
    ],
)
def test_log_viewer_query_is_validated(admin_api, query):
    assert admin_api.get(f"/api/admin/logs?{query}").status_code == 400


def test_log_viewer_with_no_log_file_yet(app, admin_api):
    import os

    os.remove(app.config["ACTIVITY_LOG_PATH"])

    assert admin_api.get("/api/admin/logs").get_json()["total"] == 0


def test_parse_line_reads_guest_and_user_lines():
    entry = parse_line("2026-11-18 18:27:03,457 | INFO | 127.0.0.1 | 2 | login | email=client@example.com\n")

    assert (entry.level, entry.ip, entry.user_id, entry.action) == ("INFO", "127.0.0.1", 2, "login")
    assert parse_line("2026-11-18 18:27:03,457 | INFO | - | - | logout | ").user_id is None
    assert parse_line("not a log line") is None
