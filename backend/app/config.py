import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
FORM_OVERHEAD_BYTES = 64 * 1024
TURNSTILE_TEST_SITE_KEY = "1x00000000000000000000AA"
TURNSTILE_TEST_SECRET_KEY = "1x0000000000000000000000000000000AA"


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
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(BACKEND_DIR, "uploads")
    MAX_UPLOAD_BYTES = MAX_UPLOAD_BYTES
    MAX_CONTENT_LENGTH = MAX_UPLOAD_BYTES + FORM_OVERHEAD_BYTES
    RATELIMIT_ENABLED = True
    RATELIMIT_APPLICATION = "100 per minute"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_HEADERS_ENABLED = False
    CAPTCHA_VERIFIER = "turnstile"
    TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "")
    TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "")
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
    TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY") or TURNSTILE_TEST_SITE_KEY
    TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY") or TURNSTILE_TEST_SECRET_KEY


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ADMIN_PASSWORD = "Test-Password-123"
    RATELIMIT_ENABLED = False
    CAPTCHA_VERIFIER = "fake"
    PAYMENT_GATEWAY = "fake"
    STRIPE_SECRET_KEY = ""
    STRIPE_WEBHOOK_SECRET = ""
    SITE_URL = "http://shop.test"


class ProductionConfig(BaseConfig):
    SESSION_COOKIE_SECURE = True
    REQUIRED_SETTINGS = (
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "SITE_URL",
        "TURNSTILE_SITE_KEY",
        "TURNSTILE_SECRET_KEY",
    )


CONFIGS: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def resolve_config(name: str | None) -> type[BaseConfig]:
    return CONFIGS.get(name or os.environ.get("FLASK_CONFIG", "development"), DevelopmentConfig)
