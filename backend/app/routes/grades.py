from datetime import date as date_type

from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
from sqlalchemy import func, select, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.models import Grade, User, Subcategory
from app.routes.helpers.decorators import require_role
from app.routes.helpers.payload import get_body, get_int, get_list, get_str

MAX_GRADE_LIMIT = 100

grades_bp = Blueprint("grades", __name__)


@grades_bp.route("/api/grades", methods=["POST"])
@require_role("teacher")
def save_grades():
    data = get_body()
    student_id = get_int(data, "student_id")
    upsert_grades = get_list(data, "upsert_grades")
    delete_grade_ids = get_list(data, "delete_grade_ids")
    grade_date = get_str(data, "date")

    if upsert_grades:
        if not grade_date:
            abort(400, "date_required")
        _validate_date(grade_date)

    if not student_id:
        abort(400, "student_id_required")
    if not upsert_grades and not delete_grade_ids:
        abort(400, "grades_payload_required")

    with get_session(write=True) as session:
        _check_student(session, student_id)

        if upsert_grades:
            _upsert_grades(session, student_id, grade_date, upsert_grades)
        if delete_grade_ids:
            _delete_grades(session, student_id, delete_grade_ids)

    return jsonify({"message": "saved"}), 201


def _validate_date(grade_date):
    try:
        parsed_date = date_type.fromisoformat(grade_date)
        # fromisoformat also parses '20240115', this rejects anything not 'YYYY-MM-DD'
        if parsed_date.isoformat() != grade_date:
            abort(400, "invalid_date_format")
    except ValueError:
        abort(400, "invalid_date_format")


# missing id or a non student id: same error for every grade route
def _check_student(session, student_id):
    student = session.get(User, student_id)
    if not student or student.role != "student":
        abort(404, "not_found")


def _upsert_grades(session, student_id: int, grade_date, upsert_grades):
    if not all(isinstance(grade, dict) for grade in upsert_grades):
        abort(400, "invalid_payload")
    subcategory_ids = [get_int(grade, "subcategory_id") for grade in upsert_grades]
    valid_subcat_ids = set(session.scalars(select(Subcategory.id).where(Subcategory.id.in_(subcategory_ids))))

    # validate all entries before writing anything, prevents partial commits
    validated = []
    for grade in upsert_grades:
        value = grade.get("value")
        # bool is a subclass of int in python: json true/false must not become 1.0/0.0
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            abort(400, "invalid_grade_value")
        value = round(value, 1)
        if not (0 <= value <= 10):
            abort(400, "grade_out_of_range")
        if grade.get("subcategory_id") not in valid_subcat_ids:
            abort(400, "invalid_subcategory_id")
        validated.append((grade.get("subcategory_id"), value))

    # one cell per subcategory: two entries for the same one is not accepted
    if len({subcategory_id for subcategory_id, _ in validated}) != len(validated):
        abort(400, "duplicate_subcategory_id")

    # single insert ... on conflict do update.
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
    if not all(type(grade_id) is int for grade_id in delete_grade_ids):
        abort(400, "invalid_payload")
    delete_grade_ids_set = set(delete_grade_ids)
    # grades with matching id, grades not belonging to this student
    matched_grades, wrong_student = session.execute(
        select(
            func.count(),
            func.count().filter(Grade.student_id != student_id),
        ).where(Grade.id.in_(delete_grade_ids_set))
    ).one()

    # every requested grade id must exist
    if matched_grades != len(delete_grade_ids_set):
        abort(404, "grades_not_found")
    if wrong_student:
        abort(400, "grades_wrong_student")

    session.execute(delete(Grade).where(Grade.id.in_(delete_grade_ids_set)))


# every grade of one student on one date, feeds the teacher grade form
# {"3": {"id": 10, "value": 7.5}}: subcat 3, grade 10
@grades_bp.route("/api/students/<int:student_id>/grades/<grade_date>")
@require_role("teacher")
def get_student_day_grades(student_id, grade_date):
    _validate_date(grade_date)

    with get_session() as session:
        _check_student(session, student_id)

        rows = session.execute(
            select(Grade.id, Grade.subcategory_id, Grade.value)
            .where(Grade.student_id == student_id, Grade.date == grade_date)
        ).all()

    return jsonify(
        {subcategory_id: {"id": grade_id, "value": value} for grade_id, subcategory_id, value in rows}
    )


@grades_bp.route("/api/students/<int:student_id>/grades")
@require_role("teacher", "student")
def get_student_grades(student_id):
    # teachers share a single student pool: any teacher may view any student's grades
    # students are restricted to their own data only
    if current_user.role == "student" and current_user.id != student_id:
        abort(403, "forbidden")  # student trying to access another student's grades

    # limit=5: 5
    # no limit, limit=abc, limit=0, limit=-1 or limit=500: 100
    limit = request.args.get("limit", MAX_GRADE_LIMIT, type=int)
    if not 1 <= limit <= MAX_GRADE_LIMIT:
        limit = MAX_GRADE_LIMIT

    with get_session() as session:
        _check_student(session, student_id)

        # row_num ranks each grade inside its subcategory, 1 = most recent:
        #   slice: 2025-07-22 -> 1, 2025-07-20 -> 2, 2025-07-17 -> 3
        #   spin:  2025-07-20 -> 1  (count restarts per subcategory)
        row_num = (
            func.row_number()
            .over(
                partition_by=Grade.subcategory_id,  # restart count for each subcategory
                order_by=Grade.date.desc(),  # 1 = most recent grade in that subcategory
            )
            .label("row_num")
        )

        # subquery: every grade id for this student, each grade tagged with its row_num
        # student with 1500 grades -> 1500 rows like (id 5400, row_num 1), (id 3240, row_num 2), ...
        ranked_grades = (
            select(Grade.id, row_num)
            .where(Grade.student_id == student_id)
            .subquery()
        )

        # top n rows per subcategory (row_num 1...limit), with subcategory and category joined, oldest to newest
        # ex: limit 5 and 45 graded subcategories = 225 flat grades, however many categories hold them
        grades = session.scalars(
            select(Grade)
            .join(ranked_grades, Grade.id == ranked_grades.c.id)
            .where(ranked_grades.c.row_num <= limit)
            .options(joinedload(Grade.subcategory).joinedload(Subcategory.category))
            .order_by(Grade.date)
        ).all()

    return jsonify(_build_grades_response(grades))


# groups a flat list of grade objects into the nested structure the frontend expects.
# sorted by cat_id then sub_id (cat ids are used only for ordering, not included in output).
# grades keep the query order, oldest to newest:
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
    subcategory = grade.subcategory
    if subcategory.category.id not in cat_map:
        cat_map[subcategory.category.id] = {"name": subcategory.category.name, "subs": {}}
    subs = cat_map[subcategory.category.id]["subs"]
    if subcategory.id not in subs:
        subs[subcategory.id] = {"name": subcategory.name, "grades": []}
    subs[subcategory.id]["grades"].append({"id": grade.id, "value": grade.value, "date": grade.date})


def _serialize(cat_map):
    return [
        {
            "category": cat["name"],
            "subcategories": [
                {"id": sub_id, "name": sub["name"], "grades": sub["grades"]}
                for sub_id, sub in sorted(cat["subs"].items())  # ascending sub_id
            ],
        }
        # cat_map: {cat_id: {"name": category name, "subs": {sub_id: {"name", "grades"}}}}, sorted by cat_id
        for _, cat in sorted(cat_map.items())
    ]
