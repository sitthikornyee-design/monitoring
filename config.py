from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional until requirements are installed
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent


def _load_local_env() -> None:
    if load_dotenv is None:
        return

    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def env_bool(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def env_path(name: str, default: Path) -> Path:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return Path(raw_value).expanduser()


_load_local_env()


class BaseConfig:
    APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
    BASE_DIR = BASE_DIR
    DATA_DIR = env_path("DATA_DIR", BASE_DIR / "data")
    RUNTIME_DIR = env_path("RUNTIME_DIR", BASE_DIR / "runtime")
    SCHEMA_PATH = env_path("SCHEMA_PATH", BASE_DIR / "schema.sql")
    DATABASE_PATH = env_path("DATABASE_PATH", RUNTIME_DIR / "workspace.sqlite3")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    WORKSPACE_NAME = os.getenv("WORKSPACE_NAME", "Sitthikorn yee's Workspace")
    SPACE_NAME = os.getenv("SPACE_NAME", "Team Space")
    DEFAULT_ACTOR = os.getenv("DEFAULT_ACTOR", "Yee")

    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = env_bool("TEMPLATES_AUTO_RELOAD", True)
    SEED_DATA = env_bool("SEED_DATA", True)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "http")


class DevelopmentConfig(BaseConfig):
    APP_ENV = "development"
    DEBUG = env_bool("FLASK_DEBUG", True)
    TESTING = False
    TEMPLATES_AUTO_RELOAD = env_bool("TEMPLATES_AUTO_RELOAD", True)
    SEED_DATA = env_bool("SEED_DATA", True)


class ProductionConfig(BaseConfig):
    APP_ENV = "production"
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    SEED_DATA = env_bool("SEED_DATA", False)
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")


def get_config():
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    if app_env == "production":
        return ProductionConfig
    return DevelopmentConfig


def validate_config(config) -> None:
    app_env = str(config.get("APP_ENV", "development")).strip().lower()
    secret_key = str(config.get("SECRET_KEY", "")).strip()

    if app_env == "production" and (not secret_key or secret_key == "dev-only-change-me"):
        raise RuntimeError("SECRET_KEY must be set to a strong value when APP_ENV=production.")
