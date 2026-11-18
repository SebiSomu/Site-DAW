from flask import Flask

from app.controllers.auth_controller import auth_bp
from app.controllers.catalog_controller import catalog_bp
from app.controllers.health_controller import health_bp
from app.controllers.payments_controller import payments_bp
from app.controllers.seo_controller import seo_bp
from app.controllers.shop_controller import shop_bp

BLUEPRINTS = (health_bp, auth_bp, catalog_bp, shop_bp, payments_bp, seo_bp)


def register_blueprints(app: Flask) -> None:
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
