from flask import Blueprint, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_session
from app.models import User
from app.routes.helpers.annotations import require_role

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    with get_session() as session:
        user = session.execute(
            select(User).filter_by(username=username)
        ).scalar_one_or_none()

        if not user or not check_password_hash(user.password_hash, password):
            abort(401, "invalid_credentials")

        login_user(user)
        return jsonify(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "locale": user.locale,
                }
            }
        )


# flask registers bottom-up, executes top-down. always innermost decorators first
@auth_bp.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logged out"})


@auth_bp.route("/api/admin/password", methods=["PATCH"])
@require_role("admin")
def change_admin_password():
    data = request.get_json() or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not check_password_hash(current_user.password_hash, old_password):
        abort(400, "wrong_current_password")

    if len(new_password) < 8:
        abort(400, "password_too_short")

    if len(new_password) > 25:
        abort(400, "password_too_long")

    with get_session(write=True) as session:
        new_pass_hash = generate_password_hash(new_password)
        admin = session.get(User, current_user.id)

        admin.password_hash = new_pass_hash
        # update the in-memory auth user so the new hash is used for the rest of this session without requiring a re-login
        current_user.password_hash = new_pass_hash

    # outside the session, already committed
    return jsonify({"message": "password updated"})


@auth_bp.route("/api/locales")
def get_locales():
    return jsonify(User.locale.type.enums)


@auth_bp.route("/api/users/locale", methods=["PATCH"])
@login_required
def set_locale():
    locale = (request.get_json() or {}).get("locale", "")
    if locale not in User.locale.type.enums:
        abort(400, "invalid_locale")
    with get_session(write=True) as session:
        user = session.get(User, current_user.id)
        user.locale = locale
    return jsonify({"message": "locale updated"})


@auth_bp.route("/api/me")
def me():
    if current_user.is_authenticated:
        response = {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "locale": current_user.locale,
        }
        return jsonify({"user": response})
    return jsonify({"user": None})
