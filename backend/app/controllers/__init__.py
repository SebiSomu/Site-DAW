from flask import Flask

from app.controllers.health_controller import health_bp

BLUEPRINTS = (health_bp,)


def register_blueprints(app: Flask) -> None:
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
