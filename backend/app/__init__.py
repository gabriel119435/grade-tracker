import logging
import os
import re

from flask import Flask, jsonify
from flask_login import LoginManager
from sqlalchemy import select, text
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from app.constants import DEFAULT_LOCALE
from app.db import get_session, engine, Base
from app.models import User, AuthUser
from app.routes.auth import auth_bp
from app.routes.categories import categories_bp
from app.routes.grades import grades_bp
from app.routes.seed import seed_bp
from app.routes.students import students_bp
from app.routes.teachers import teachers_bp
from app.validation import password_error

login_manager = LoginManager()
logger = logging.getLogger(__name__)


def create_app():
    # same as flask default format: [2026-09-28 16:26:08,926] INFO in __init__: admin created
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    _apply_migrations()
    _create_admin()  # needs the final schema, so it runs after every migration

    app = Flask(__name__)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        logger.warning("using insecure default secret")
        secret_key = "dev-default-value"
    app.secret_key = secret_key
    # session cookie is never sent on requests coming from other sites
    app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
    # SESSION_COOKIE_SECURE=1: session cookie only travels over https, for deploys behind https
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE") == "1"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(session_id):
        # session_id comes from AuthUser.get_id(): "<id> <last 10 hash chars>"
        parts = session_id.split(" ")
        if len(parts) != 2 or not parts[0].isdigit():
            return None
        user_id, hash_tail = parts
        with get_session() as session:
            # this query is executed for every single request
            user = session.get(User, int(user_id))
            # missing user or changed password: session is no longer valid
            if not user or user.password_hash[-10:] != hash_tail:
                return None
            # returns entity not managed by sqlalchemy
            return AuthUser.from_user(user)

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        if re.fullmatch(r"[a-z_]+", e.description):
            return jsonify({"error": e.description}), e.code
        # "Method Not Allowed" -> "method_not_allowed"
        return jsonify({"error": e.name.lower().replace(" ", "_")}), e.code

    _register_blueprints(app)

    return app


# migrations are by default idempotent, are always applied on startup
def _apply_migrations():
    _migration_000_create_db()
    _migration_001_add_locale()


def _migration_000_create_db():
    Base.metadata.create_all(engine)  # idempotent: no op if tables already exist


def _migration_001_add_locale():
    with engine.connect() as conn:
        # runs after 000, so the users table always exists here
        columns =[row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if "locale" not in columns:
            conn.execute(text(f"ALTER TABLE users ADD COLUMN locale TEXT NOT NULL DEFAULT '{DEFAULT_LOCALE}'"))
            conn.commit()


# data step, not a migration: runs on every startup, creates the admin only if missing
def _create_admin():
    with get_session(write=True) as session:
        if session.scalar(select(User).filter_by(username="admin")):
            # admin already exists, ADMIN_PASS is not read
            return
        session.add(
            User(
                username="admin",
                password_hash=generate_password_hash(_get_admin_pass()),
                role="admin",
            )
        )
    logger.info("admin created")


def _get_admin_pass():
    # ADMIN_PASS unset or empty: use a known weak default, for local dev only
    admin_pass = os.environ.get("ADMIN_PASS") or "admin pass"
    # same rules as every other password, for both the env value and the default
    error = password_error(admin_pass)
    if error:
        raise ValueError(f"ADMIN_PASS: {error}")
    return admin_pass


def _register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(seed_bp)
