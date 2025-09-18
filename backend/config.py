"""Application configuration for Top Scoot backend."""

from __future__ import annotations

import os
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

# Check if running on Heroku (DYNO environment variable is set)
if 'DYNO' in os.environ:
    # On Heroku, use cwd as root for proper path resolution
    DEFAULT_DB_PATH = Path.cwd() / "data" / "top-scoot.sqlite3"
else:
    # Local development
    DEFAULT_DB_PATH = ROOT_DIR / "data" / "top-scoot.sqlite3"

def validate_database_config(db_path: Path) -> None:
    """Validate database configuration and log relevant information."""
    logging.info(f"Database path set to: {db_path}")
    logging.info(f"Database file exists: {db_path.exists()}")
    if not db_path.exists():
        logging.warning("Database file not found at the specified path!")
        # Also log the parent directory contents for debugging
        parent_dir = db_path.parent
        if parent_dir.exists():
            logging.info(f"Contents of database directory ({parent_dir}): {list(parent_dir.iterdir())}")
        else:
            logging.warning(f"Database directory does not exist: {parent_dir}")

DEFAULT_CORS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"

def _resolve_db_path(raw: str | Path | None) -> Path:
    if raw is None:
        return DEFAULT_DB_PATH
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path


class Config:
    SECRET_KEY = os.environ.get("TOPSCOOT_SECRET", "dev-secret")
    SESSION_COOKIE_NAME = "topscoot_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    DATABASE_PATH = _resolve_db_path(os.environ.get("TOPSCOOT_DATABASE"))
    DATABASE_READONLY = os.environ.get("TOPSCOOT_DATABASE_READONLY", "0") in {"1", "true", "True"}
    CORS_ORIGINS = os.environ.get("TOPSCOOT_CORS_ORIGINS", DEFAULT_CORS)
    JSON_SORT_KEYS = False
    
    # MariaDB Configuration
    DB_HOST = os.environ.get("DB_HOST", "scootrate-mariadb-wmclth")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "scootrate")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "secret")
    DB_NAME = os.environ.get("DB_NAME", "scootrate")

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
