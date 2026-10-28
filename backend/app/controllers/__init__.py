from flask import Flask

from app.controllers.auth_controller import auth_bp
from app.controllers.health_controller import health_bp

BLUEPRINTS = (health_bp, auth_bp)


def register_blueprints(app: Flask) -> None:
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
