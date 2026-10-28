import pytest

from app import create_app
from app.extensions import db as database
from app.seed import DatabaseSeeder


class ApiClient:
    def __init__(self, client) -> None:
        self.client = client
        self.csrf_token = client.get("/api/csrf").get_json()["csrf_token"]

    def get(self, url: str):
        return self.client.get(url)

    def post(self, url: str, json: dict | None = None):
        return self.client.post(url, json=json, headers={"X-CSRFToken": self.csrf_token})


@pytest.fixture()
def app(tmp_path):
    application = create_app("testing", {"ACTIVITY_LOG_PATH": str(tmp_path / "activity.log")})
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
def activity_log(app):
    def read() -> str:
        with open(app.config["ACTIVITY_LOG_PATH"], encoding="utf-8") as log_file:
            return log_file.read()

    return read
