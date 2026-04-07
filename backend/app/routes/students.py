from flask import Blueprint, request, jsonify
from sqlalchemy import func, select

from app.db import get_session
from app.models import User, Grade
from app.routes.helpers.annotations import require_role
from app.routes.helpers.users import create_user, delete_user

students_bp = Blueprint("students", __name__)


@students_bp.route("/api/students")
@require_role("teacher")
def get_students():
    with get_session() as session:
        rows = session.execute(
            select(User, func.count(Grade.id).label("grade_count"))
            .outerjoin(Grade, Grade.student_id == User.id)
            .where(User.role == "student")
            .group_by(User.id)
            .order_by(User.id)
        ).all()
    return jsonify(
        [
            {"id": s.id, "username": s.username, "grade_count": count}
            for s, count in rows
        ]
    )


@students_bp.route("/api/students", methods=["POST"])
@require_role("teacher")
def create_student():
    return create_user("student", request.get_json() or {})


@students_bp.route("/api/students/<int:student_id>", methods=["DELETE"])
@require_role("teacher")
def delete_student(student_id):
    return delete_user(student_id, "student")
