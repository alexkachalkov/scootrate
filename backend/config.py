"""Application configuration for Top Scoot backend."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT_DIR / "data" / "top-scoot.sqlite3"
DEFAULT_CORS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"


class Config:
    SECRET_KEY = os.environ.get("TOPSCOOT_SECRET", "dev-secret")
    SESSION_COOKIE_NAME = "topscoot_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    DATABASE_PATH = Path(os.environ.get("TOPSCOOT_DATABASE", DEFAULT_DB_PATH))
    CORS_ORIGINS = os.environ.get("TOPSCOOT_CORS_ORIGINS", DEFAULT_CORS)
    JSON_SORT_KEYS = False


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True


class DevelopmentConfig(Config):
    DEBUG = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": Config,
}


def get_config(config_name: str | None = None) -> type[Config]:
    if not config_name:
        config_name = os.environ.get("TOPSCOOT_ENV", "development")
    return config_by_name.get(config_name, Config)
