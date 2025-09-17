from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from config import get_config
from db import init_app as init_db
from routes.public import bp as public_bp
from routes.admin import bp as admin_bp


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
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

    @app.get("/")
    def index() -> dict[str, str]:
        return {"message": "Top Scoot backend is running"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
