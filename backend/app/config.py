import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@gemuricalamama.ro")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    TESTING = False
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    ADMIN_PASSWORD = "Parola-Test-123"


class ProductionConfig(BaseConfig):
    pass


CONFIGS: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def resolve_config(name: str | None) -> type[BaseConfig]:
    return CONFIGS.get(name or os.environ.get("FLASK_CONFIG", "development"), DevelopmentConfig)
