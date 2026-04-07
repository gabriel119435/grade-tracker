from datetime import date as date_type

from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
from sqlalchemy import func, select, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.models import Grade, User, Subcategory
from app.routes.helpers.annotations import require_role

MAX_GRADE_LIMIT = 100

grades_bp = Blueprint("grades", __name__)


@grades_bp.route("/api/grades", methods=["POST"])
@require_role("teacher")
def create_grades():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    upsert_grades = data.get("upsert_grades", [])
    delete_grade_ids = data.get("delete_grade_ids", [])
    grade_date = data.get("date", date_type.today().isoformat())

    try:
        date_type.fromisoformat(grade_date)
    except ValueError:
        abort(400, "invalid_date_format")

    if not student_id:
        abort(400, "student_id_required")
    if not upsert_grades and not delete_grade_ids:
        abort(400, "grades_payload_required")

    with get_session(write=True) as session:
        student = session.get(User, student_id)
        if not student or student.role != "student":
            abort(400, "invalid_student_id")

        if upsert_grades:
            _upsert_grades(session, student_id, grade_date, upsert_grades)
        if delete_grade_ids:
            _delete_grades(session, student_id, delete_grade_ids)

    return jsonify({"message": "saved"}), 201


def _upsert_grades(session, student_id: int, grade_date, upsert_grades):
    subcategory_ids = [grade.get("subcategory_id") for grade in upsert_grades]
    valid_subcat_ids = set(session.scalars(select(Subcategory.id).where(Subcategory.id.in_(subcategory_ids))))

    # validate all entries before writing anything, prevents partial commits
    validated = []
    for grade in upsert_grades:
        try:
            value = round(float(grade["value"]), 1)
        except (ValueError, TypeError):
            abort(400, "invalid_grade_value")
        if not (0 <= value <= 10):
            abort(400, "grade_out_of_range")
        if grade.get("subcategory_id") not in valid_subcat_ids:
            abort(400, "invalid_subcategory_id")
        validated.append((grade.get("subcategory_id"), value))

    # single insert ... on conflict do update;
    # conflict target mirrors unique constraint on 'student_id', 'subcategory_id' and 'date'
    upsert = sqlite_insert(Grade).values(
        [
            {
                "student_id": student_id,
                "teacher_id": current_user.id,
                "subcategory_id": subcategory_id,
                "value": grade_value,
                "date": grade_date,
            }
            for subcategory_id, grade_value in validated
        ]
    )
    session.execute(
        upsert.on_conflict_do_update(
            index_elements=["student_id", "subcategory_id", "date"],
            # on conflict, overwrite value and teacher with the incoming values
            set_={
                "value": upsert.excluded.value,
                "teacher_id": upsert.excluded.teacher_id,
            },
        )
    )


def _delete_grades(session, student_id: int, delete_grade_ids):
    # grades with matching id, grades not belonging to this student, grades not owned by current teacher
    matched_grades, wrong_student, wrong_teacher = session.execute(
        select(
            func.count(),
            func.count().filter(Grade.student_id != student_id),
            func.count().filter(Grade.teacher_id != current_user.id),
        ).where(Grade.id.in_(delete_grade_ids))
    ).one()

    if matched_grades != len(delete_grade_ids):
        abort(404, "grades_not_found")
    if wrong_student:
        abort(400, "grades_wrong_student")
    if wrong_teacher:
        abort(403, "forbidden")

    session.execute(delete(Grade).where(Grade.id.in_(delete_grade_ids)))


@grades_bp.route("/api/students/<int:student_id>/grades")
@require_role("teacher", "student")
def get_student_grades(student_id):
    # teachers share a single student pool: any teacher may view any student's grades
    # students are restricted to their own data only
    if current_user.role == "student" and current_user.id != student_id:
        abort(403, "forbidden")  # student trying to access another student's grades

    limit = min(request.args.get("limit", MAX_GRADE_LIMIT, type=int), MAX_GRADE_LIMIT)

    with get_session() as session:
        # numbers each grade 1...n within its subcategory, most recent first
        row_num = (
            func.row_number()
            .over(
                partition_by=Grade.subcategory_id,  # restart count for each subcategory
                order_by=Grade.date.desc(),  # 1 = most recent grade in that subcategory
            )
            .label("row_num")
        )

        # subquery: every grade for this student, each grade tagged with its row_num
        ranked_grades = (
            select(Grade.id, row_num)
            .where(Grade.student_id == student_id)
            .subquery()
        )

        # keep only the top n rows per subcategory (row_num 1...limit)
        grade_ids = session.scalars(
            select(ranked_grades.c.id).where(ranked_grades.c.row_num <= limit)
        ).all()

        # fetch the selected grades with subcategory+category joined in one query
        grades = session.scalars(
            select(Grade)
            .options(joinedload(Grade.subcategory).joinedload(Subcategory.category))
            .where(Grade.id.in_(grade_ids))
            .order_by(Grade.date)
        ).all()

    return jsonify(_build_grades_response(grades))


# groups a flat list of grade objects into the nested structure the frontend expects,
# sorted by cat_id then sub_id (ids are used only for ordering; not included in output):
# [
#     {'category': 'forehand', 'subcategories': [{'id': 10, 'name': 'spin',     'grades': [{'id': 5, 'value': 8.5, 'date': '2024-01-15'}]}]},
#     {'category': 'serve',    'subcategories': [{'id': 20, 'name': 'position', 'grades': [{'id': 6, 'value': 7.0, 'date': '2024-01-15'}]}]}
# ]
def _build_grades_response(grades):
    cat_map = {}
    for grade in grades:
        _accumulate(cat_map, grade)
    return _serialize(cat_map)


def _accumulate(cat_map, grade):
    cat_id = grade.subcategory.category.id
    sub_id = grade.subcategory.id
    if cat_id not in cat_map:
        cat_map[cat_id] = {"name": grade.subcategory.category.name, "subs": {}}
    cat_map[cat_id]["subs"].setdefault(sub_id, {"name": grade.subcategory.name, "grades": []})
    cat_map[cat_id]["subs"][sub_id]["grades"].append({"id": grade.id, "value": grade.value, "date": grade.date})


def _serialize(cat_map):
    return [
        {
            "category": cat["name"],
            "subcategories": [
                {"id": sub_id, "name": sub["name"], "grades": sub["grades"]}
                for sub_id, sub in sorted(cat["subs"].items())  # ascending sub_id
            ],
        }
        for cat_id, cat in sorted(cat_map.items())  # ascending cat_id
    ]
