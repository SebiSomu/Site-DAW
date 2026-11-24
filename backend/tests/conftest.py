import pytest

from app import create_app
from app.extensions import db as database
from app.seed import DatabaseSeeder
from app.security import CAPTCHA_HEADER
from app.services.captcha import FAKE_CAPTCHA_TOKEN


class ApiClient:
    def __init__(self, client) -> None:
        self.client = client
        self.csrf_token = self.get("/api/csrf").get_json()["csrf_token"]

    @property
    def write_headers(self) -> dict[str, str]:
        return {"X-CSRFToken": self.csrf_token, CAPTCHA_HEADER: FAKE_CAPTCHA_TOKEN}

    def _in_own_context(self, send, *args, **kwargs):
        with self.client.application.app_context():
            return send(*args, **kwargs)

    def get(self, url: str):
        return self._in_own_context(self.client.get, url)

    def post(self, url: str, json: dict | None = None):
        return self._in_own_context(self.client.post, url, json=json, headers=self.write_headers)

    def put(self, url: str, json: dict | None = None):
        return self._in_own_context(self.client.put, url, json=json, headers=self.write_headers)

    def patch(self, url: str, json: dict | None = None):
        return self._in_own_context(self.client.patch, url, json=json, headers=self.write_headers)

    def post_form(self, url: str, data: dict):
        return self._in_own_context(
            self.client.post,
            url,
            data=data,
            headers=self.write_headers,
            content_type="multipart/form-data",
        )

    def delete(self, url: str):
        return self._in_own_context(self.client.delete, url, headers=self.write_headers)


@pytest.fixture()
def app(tmp_path):
    application = create_app(
        "testing",
        {"ACTIVITY_LOG_PATH": str(tmp_path / "activity.log"), "UPLOAD_FOLDER": str(tmp_path / "uploads")},
    )
    with application.app_context():
        database.create_all()
        yield application
        database.session.remove()
        database.drop_all()


@pytest.fixture()
def session(app):
    return database.session


@pytest.fixture()
def seeded(app):
    DatabaseSeeder().run(include_demo_client=True)
    return database.session


@pytest.fixture()
def api(app, seeded):
    return ApiClient(app.test_client())


@pytest.fixture()
def new_api(app, seeded):
    return lambda: ApiClient(app.test_client())


@pytest.fixture()
def activity_log(app):
    def read() -> str:
        with open(app.config["ACTIVITY_LOG_PATH"], encoding="utf-8") as log_file:
            return log_file.read()

    return read
