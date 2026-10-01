from flask import Blueprint, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_session
from app.models import AuthUser, User
from app.routes.helpers.decorators import require_role
from app.routes.helpers.payload import get_body, get_str
from app.routes.helpers.users import password_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = get_body()
    username = get_str(data, "username", "").strip()
    password = get_str(data, "password", "")

    with get_session() as session:
        user = session.execute(
            select(User).filter_by(username=username)
        ).scalar_one_or_none()

        if not user or not check_password_hash(user.password_hash, password):
            abort(401, "invalid_credentials")

        login_user(AuthUser.from_user(user))
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
    return jsonify({"message": "password updated"})


@auth_bp.route("/api/locales")
def get_locales():
    return jsonify(User.locale.type.enums)


@auth_bp.route("/api/users/locale", methods=["PATCH"])
@login_required
def set_locale():
    locale = get_str(get_body(), "locale")
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
