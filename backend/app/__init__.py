import logging
import os
import re

from flask import Flask, jsonify
from flask_login import LoginManager
from sqlalchemy import select, text
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from app.db import get_session, engine, Base
from app.models import User, AuthUser
from app.routes.auth import auth_bp
from app.routes.categories import categories_bp
from app.routes.grades import grades_bp
from app.routes.helpers.users import password_error
from app.routes.seed import seed_bp
from app.routes.students import students_bp
from app.routes.teachers import teachers_bp

login_manager = LoginManager()
logger = logging.getLogger(__name__)


def create_app():
    # flask default format: [2026-09-28 16:26:08,926] INFO in __init__: admin created
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    apply_migrations()

    app = Flask(__name__)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        logger.warning("using insecure default secret")
        secret_key = "dev-default-value"
    app.secret_key = secret_key

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        with get_session() as session:
            # this query is executed for every single request
            user = session.execute(
                select(User).filter_by(id=int(user_id))
            ).scalar_one_or_none()
            if not user:
                return None
            # returns entity not managed by sqlalchemy
            return AuthUser.from_user(user)

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "unauthorized"}), 401

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        if re.fullmatch(r"[a-z_]+", e.description):
            return jsonify({"error": e.description}), e.code
        # "Method Not Allowed" -> "method_not_allowed"
        return jsonify({"error": e.name.lower().replace(" ", "_")}), e.code

    _register_blueprints(app)

    return app


# migrations are by default idempotent, are always applied on startup
def apply_migrations():
    _migration_000_create_db()
    _migration_001_add_locale()


def _migration_000_create_db():
    Base.metadata.create_all(engine)  # idempotent: no op if tables already exist

    # ADMIN_PASS unset or empty: use a known weak default, for local dev only
    admin_pass = os.environ.get("ADMIN_PASS") or "admin-pass"
    # same rules as every other password, for both the env value and the default
    error = password_error(admin_pass)
    if error:
        raise ValueError(f"ADMIN_PASS: {error}")

    with get_session(write=True) as session:
        if session.execute(
                select(User).filter_by(username="admin")
        ).scalar_one_or_none():
            # admin already exists, nothing to do
            return
        session.add(
            User(
                username="admin",
                password_hash=generate_password_hash(admin_pass),
                role="admin",
            )
        )
    logger.info("admin created")


def _migration_001_add_locale():
    with engine.connect() as conn:
        table_exists = conn.execute(text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'")).scalar()
        if not table_exists:
            return
        columns = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if "locale" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN locale TEXT NOT NULL DEFAULT 'pt-br'"))
            conn.commit()


def _register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(seed_bp)
