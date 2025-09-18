from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, send_from_directory
from flask_cors import CORS

from config import get_config
# Импортируем правильный модуль базы данных в зависимости от конфигурации
import os

# Определяем, какую систему баз данных использовать
if os.environ.get("USE_MARIADB", "false").lower() == "true":
    from db_mariadb import init_app as init_db
else:
    from db import init_app as init_db

from routes.public import bp as public_bp
from routes.admin import bp as admin_bp

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BACKEND_DIR.parent / "frontend" / "dist"

def create_app(config_name: str | None = None) -> Flask:
    static_folder = str(FRONTEND_DIST) if FRONTEND_DIST.exists() else None
    app = Flask(__name__, static_folder=static_folder, static_url_path="")
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    app.config["DATABASE_PATH"] = str(config_class.DATABASE_PATH)

    origins = app.config.get("CORS_ORIGINS")
    if isinstance(origins, str):
        origins = [origin.strip() for origin in origins.split(",") if origin.strip()]
    if not origins:
        origins = ["http://localhost:5173"]
    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    init_db(app)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    if app.static_folder:

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path: str):
            if path.startswith("api/"):
                abort(404)
            target_path = FRONTEND_DIST / path
            if path and target_path.exists():
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, "index.html")

    else:

        @app.get("/")
        def index() -> dict[str, str]:
            return {"message": "Top Scoot backend is running"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
