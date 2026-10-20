from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_user, logout_user
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.constants import LOCALES
from app.db import get_session
from app.models import AuthUser, User
from app.routes.helpers.decorators import require_role
from app.routes.helpers.payload import get_body, get_str
from app.validation import password_error

auth_bp = Blueprint("auth", __name__)

# admin password when ADMIN_PASS is unset or empty, a known weak default for local dev only
DEFAULT_ADMIN_PASS = "admin pass"
# a missing user still runs one scrypt check, so response time doesn't reveal which usernames exist
_DUMMY_HASH = generate_password_hash(DEFAULT_ADMIN_PASS)


# public user fields sent to the frontend, never the password hash
def _build_user_json(user):
    return {"id": user.id, "username": user.username, "role": user.role, "locale": user.locale}


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = get_body()
    username = get_str(data, "username", "").strip()
    password = get_str(data, "password", "")

    with get_session() as session:
        user = session.scalar(select(User).filter_by(username=username))

        password_hash = user.password_hash if user else _DUMMY_HASH
        if not check_password_hash(password_hash, password) or not user:
            abort(401, "invalid_credentials")

        auth_user = AuthUser.from_user(user)

    login_user(auth_user)
    return jsonify({"user": _build_user_json(auth_user)})


# @route stays on top: decorators apply bottom-up. if swapped, flask would register the unprotected function
@auth_bp.route("/api/logout", methods=["POST"])
@require_role()
def logout():
    logout_user()
    return jsonify({"message": "logged out"})


@auth_bp.route("/api/admin/password", methods=["PATCH"])
@require_role("admin")
def change_admin_password():
    data = get_body()
    old_password = get_str(data, "old_password", "")
    new_password = get_str(data, "new_password", "")

    if not check_password_hash(current_user.password_hash, old_password):
        abort(400, "wrong_current_password")

    error = password_error(new_password)
    if error:
        abort(400, error)

    with get_session(write=True) as session:
        new_pass_hash = generate_password_hash(new_password)
        admin = session.get(User, current_user.id)

        admin.password_hash = new_pass_hash

    # outside the session, already committed
    # the new hash invalidates current session, so it is reissued to stay logged in
    login_user(AuthUser.from_user(admin))
    return jsonify({"message": "password updated"})


@auth_bp.route("/api/users/locale", methods=["PATCH"])
@require_role()
def set_locale():
    locale = get_str(get_body(), "locale")
    if locale not in LOCALES:
        abort(400, "invalid_locale")
    with get_session(write=True) as session:
        user = session.get(User, current_user.id)
        user.locale = locale
    return jsonify({"message": "locale updated"})


@auth_bp.route("/api/me")
def me():
    return jsonify({"user": _build_user_json(current_user) if current_user.is_authenticated else None})
