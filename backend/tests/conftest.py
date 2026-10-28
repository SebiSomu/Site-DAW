import pytest

from app import create_app
from app.extensions import db as database
from app.seed import DatabaseSeeder


@pytest.fixture()
def app():
    application = create_app("testing")
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
