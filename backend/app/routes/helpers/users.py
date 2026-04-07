from flask import jsonify, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import User


def create_user(role, data):
    # role is trusted, caller must guard with @require_role before reaching here
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        abort(400, "username_and_password_required")

    if username != username.strip():
        abort(400, "username_spaces")

    if len(username) > 25:
        abort(400, "username_too_long")

    # no minimum length for usernames: they are not secrets, so short names and initials are valid
    if len(password) < 8:
        abort(400, "password_too_short")

    if len(password) > 25:
        abort(400, "password_too_long")

    try:
        with get_session(write=True) as session:
            session.add(
                User(
                    username=username,
                    password_hash=generate_password_hash(password),
                    role=role,
                )
            )
        return jsonify({"message": "created"}), 201
    except IntegrityError:
        abort(409, "username_exists")




def delete_user(user_id, role):
    # role is trusted, caller must guard with @require_role before reaching here
    with get_session(write=True) as session:
        user = session.get(User, user_id)
        if not user or user.role != role:
            abort(404, "not_found")
        session.delete(user)

    return jsonify({"message": "deleted"})
