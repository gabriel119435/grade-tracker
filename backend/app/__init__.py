import logging
import os
import re

from flask import Flask, jsonify
from flask_login import LoginManager
from sqlalchemy import select
from werkzeug.exceptions import HTTPException

from app.arena import create_arena
from app.db import get_session
from app.migrations import apply_migrations
from app.models import Arena, AuthUser, User
from app.routes.arenas import arenas_bp
from app.routes.auth import auth_bp
from app.routes.categories import categories_bp
from app.routes.grades import grades_bp
from app.routes.seed import seed_bp
from app.routes.students import students_bp
from app.routes.teachers import teachers_bp
from app.settings import DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS, DEFAULT_ARENA_NAME, check_settings

login_manager = LoginManager()
logger = logging.getLogger(__name__)


def create_app():
    # same as flask default format: [2026-09-28 16:26:08,926] INFO in __init__: default arena created
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    # fails startup on an invalid env value, before any of them is used
    check_settings()
    apply_migrations()
    # needs the final schema, so it runs after every migration
    _create_default_arena()

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
        # a snake_case description is an error code, sent as is: a typo reaches the ui as "<code> not found", by design
        # any other text, like werkzeug's default sentences, falls back to the status name below
        if re.fullmatch(r"[a-z_]+", e.description):
            return jsonify({"error": e.description}), e.code
        # "Method Not Allowed" -> "method_not_allowed"
        return jsonify({"error": e.name.lower().replace(" ", "_")}), e.code

    _register_blueprints(app)

    return app


# data step, not a migration: runs on every startup, creates the default arena and its admin only on an empty db
def _create_default_arena():
    with get_session() as session:
        # any arena exists, DEFAULT_ARENA_NAME, DEFAULT_ADMIN_NAME and DEFAULT_ADMIN_PASS are not used
        if session.scalar(select(Arena.id)):
            return
    create_arena(DEFAULT_ARENA_NAME, DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS)
    logger.info("default arena created")


def _register_blueprints(app):
    app.register_blueprint(arenas_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(seed_bp)
