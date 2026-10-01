from flask import Blueprint

from app.models import Grade
from app.routes.helpers.decorators import require_role
from app.routes.helpers.payload import get_body
from app.routes.helpers.users import create_user, delete_user, list_users

students_bp = Blueprint("students", __name__)


@students_bp.route("/api/students")
@require_role("teacher")
def get_students():
    return list_users("student", Grade.student_id)


@students_bp.route("/api/students", methods=["POST"])
@require_role("teacher")
def create_student():
    return create_user("student", get_body())


@students_bp.route("/api/students/<int:student_id>", methods=["DELETE"])
@require_role("teacher")
def delete_student(student_id):
    return delete_user(student_id, "student")
