import os

from flask import Flask

from app.cli import register_cli
from app.controllers import register_blueprints
from app.config import resolve_config
from app.extensions import db, migrate


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(resolve_config(config_name))
    os.makedirs(app.instance_path, exist_ok=True)

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        database_path = os.path.join(app.instance_path, "gemuri.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from app import models

    register_blueprints(app)
    register_cli(app)
    return app
