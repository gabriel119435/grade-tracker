from flask import jsonify, abort
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.constants import USERNAME_MAX_LENGTH
from app.db import get_session
from app.models import Grade, User
from app.routes.helpers.payload import get_str
from app.validation import password_error, validate_word_size


def list_users(role, grade_fk):
    # grade_fk: Grade.teacher_id counts grades given, Grade.student_id counts grades received
    with get_session() as session:
        rows = session.execute(
            select(User, func.count(Grade.id))
            .outerjoin(Grade, grade_fk == User.id)
            .where(User.role == role)
            .group_by(User.id)
            .order_by(User.id)
        ).all()
    return jsonify([{"id": user.id, "username": user.username, "grade_count": count} for user, count in rows])


def create_user(role, data):
    # role is trusted, caller must guard with @require_role before reaching here
    username = get_str(data, "username")
    password = get_str(data, "password")

    if not username or not password:
        abort(400, "username_and_password_required")

    if username != username.strip():
        abort(400, "username_spaces")

    # no minimum length for usernames: they are not secrets, so short names and initials are valid
    if len(username) > USERNAME_MAX_LENGTH:
        abort(400, "username_too_long")

    validate_word_size(username)

    error = password_error(password)
    if error:
        abort(400, error)

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
