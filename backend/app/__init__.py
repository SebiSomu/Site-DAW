import os

from flask import Flask

from app.cli import register_cli
from app.controllers import register_blueprints
from app.config import resolve_config
from app.errors import register_error_handlers
from app.extensions import csrf, db, login_manager, migrate
from app.security import load_user, reject_anonymous
from app.services.activity_logger import activity_logger


def create_app(config_name: str | None = None, overrides: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(resolve_config(config_name))
    app.config.update(overrides or {})
    os.makedirs(app.instance_path, exist_ok=True)

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        database_path = os.path.join(app.instance_path, "jams.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    login_manager.unauthorized_handler(reject_anonymous)
    activity_logger.init_app(app)

    from app import models

    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)
    return app
