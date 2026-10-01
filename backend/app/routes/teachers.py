from flask import Blueprint

from app.models import Grade
from app.routes.helpers.decorators import require_role
from app.routes.helpers.payload import get_body
from app.routes.helpers.users import create_user, delete_user, list_users

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.route("/api/teachers")
@require_role("admin")
def get_teachers():
    return list_users("teacher", Grade.teacher_id)


@teachers_bp.route("/api/teachers", methods=["POST"])
@require_role("admin")
def create_teacher():
    return create_user("teacher", get_body())


@teachers_bp.route("/api/teachers/<int:teacher_id>", methods=["DELETE"])
@require_role("admin")
def delete_teacher(teacher_id):
    return delete_user(teacher_id, "teacher")
