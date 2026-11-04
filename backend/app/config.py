import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_TIME_LIMIT = None
    ACTIVITY_LOG_PATH = os.environ.get("ACTIVITY_LOG_PATH") or os.path.join(BACKEND_DIR, "logs", "activity.log")
    PAYMENT_GATEWAY = "stripe"
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    SITE_URL = os.environ.get("SITE_URL", "")
    REQUIRED_SETTINGS: tuple[str, ...] = ()
    TESTING = False
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SITE_URL = os.environ.get("SITE_URL") or "http://localhost:5173"


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ADMIN_PASSWORD = "Test-Password-123"
    PAYMENT_GATEWAY = "fake"
    STRIPE_SECRET_KEY = ""
    STRIPE_WEBHOOK_SECRET = ""
    SITE_URL = "http://shop.test"


class ProductionConfig(BaseConfig):
    SESSION_COOKIE_SECURE = True
    REQUIRED_SETTINGS = ("STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "SITE_URL")


CONFIGS: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def resolve_config(name: str | None) -> type[BaseConfig]:
    return CONFIGS.get(name or os.environ.get("FLASK_CONFIG", "development"), DevelopmentConfig)
