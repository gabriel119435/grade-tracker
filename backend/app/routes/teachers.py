from flask import Blueprint, request, jsonify
from sqlalchemy import func, select

from app.db import get_session
from app.models import User, Grade
from app.routes.helpers.annotations import require_role
from app.routes.helpers.users import create_user, delete_user

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.route("/api/teachers")
@require_role("admin")
def get_teachers():
    with get_session() as session:
        rows = session.execute(
            select(User, func.count(Grade.id).label("grade_count"))
            .outerjoin(Grade, Grade.teacher_id == User.id)
            .where(User.role == "teacher")
            .group_by(User.id)
            .order_by(User.id)
        ).all()
    return jsonify(
        [
            {"id": t.id, "username": t.username, "grade_count": count}
            for t, count in rows
        ]
    )


@teachers_bp.route("/api/teachers", methods=["POST"])
@require_role("admin")
def create_teacher():
    return create_user("teacher", request.get_json() or {})


@teachers_bp.route("/api/teachers/<int:teacher_id>", methods=["DELETE"])
@require_role("admin")
def delete_teacher(teacher_id):
    return delete_user(teacher_id, "teacher")
