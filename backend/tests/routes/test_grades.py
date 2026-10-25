from datetime import date as date_type
from datetime import timedelta

import pytest
from sqlalchemy import insert, select
from werkzeug.security import generate_password_hash

from app.arena import create_arena
from app.db import get_session
from app.models import Arena, Category, Grade, Subcategory, User
from app.settings import DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS
from tests.helpers import PASSWORD, login

DEFAULT_DAY = "2024-01-15"
# id that no row has, for not found cases
MISSING_ID = 1000
# second arena name, built by _make_other_arena
OTHER_ARENA = "arena2"


def _save_grades(client, payload):
    return client.post("/api/grades", json=payload)


def _get_upsert_payload(grade_context, value=8.0, date=DEFAULT_DAY, subcategory_id=None):
    return {
        "student_id": grade_context["student1_id"],
        "date": date,
        "upsert_grades": [{"subcategory_id": subcategory_id or grade_context["subcategory1_id"], "value": value}],
    }


def _get_delete_payload(grade_context, ids, student_id=None):
    return {"student_id": student_id or grade_context["student1_id"], "delete_grade_ids": ids}


def _get_history(client, grade_context, query=""):
    return client.get(f"/api/students/{grade_context['student1_id']}/grades{query}").get_json()


def _get_first_subcategory_grades(client, grade_context, query=""):
    # grades of the first subcategory of the first category, the only one with grades in these tests
    return _get_history(client, grade_context, query)[0]["subcategories"][0]["grades"]


def _get_day_grades(client, student_id, date):
    return client.get(f"/api/students/{student_id}/grades/{date}")


def _get_day_grade_id(client, grade_context, date=DEFAULT_DAY):
    day_grades = _get_day_grades(client, grade_context["student1_id"], date).get_json()
    return day_grades[str(grade_context["subcategory1_id"])]["id"]


def _assert_error(res, status, error):
    assert res.status_code == status
    assert res.get_json() == {"error": error}


def _assert_saved(res):
    assert res.status_code == 201
    assert res.get_json() == {"message": "saved"}


def _make_daily_dates(count):
    # count consecutive days from 2023-01-01, oldest first, as 'YYYY-MM-DD'
    return [(date_type(2023, 1, 1) + timedelta(days=i)).isoformat() for i in range(count)]


def _create_grade(client, grade_context):
    # saves one grade as the logged-in teacher and returns its id
    _assert_saved(_save_grades(client, _get_upsert_payload(grade_context)))
    return _get_day_grade_id(client, grade_context)


def _insert_grades(grade_context, dates, subcategory_key="subcategory1_id"):
    # direct db insert, one grade per date in the given subcategory, value 5.0
    with get_session(write=True) as session:
        session.execute(
            insert(Grade),
            [
                {
                    "value": 5.0,
                    "date": date,
                    "student_id": grade_context["student1_id"],
                    "teacher_id": grade_context["teacher1_id"],
                    "subcategory_id": grade_context[subcategory_key],
                }
                for date in dates
            ],
        )


def _make_other_arena():
    # second arena reusing grade_context's names: teacher1, student1, serve and slice
    create_arena(OTHER_ARENA, DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS)
    with get_session(write=True) as session:
        arena_id = session.scalar(select(Arena.id).filter_by(name=OTHER_ARENA))
        p_hash = generate_password_hash(PASSWORD)
        teacher = User(arena_id=arena_id, username="teacher1", password_hash=p_hash, role="teacher")
        student = User(arena_id=arena_id, username="student1", password_hash=p_hash, role="student")
        category = Category(name="serve", arena_id=arena_id)
        session.add_all([teacher, student, category])
        session.flush()
        subcategory = Subcategory(name="slice", category_id=category.id)
        session.add(subcategory)
        session.flush()
        return {"student_id": student.id, "subcategory_id": subcategory.id}


@pytest.mark.parametrize("date", [None, ""])
def test_upsert_rejects_missing_date(client, grade_context, date):
    login(client)
    res = _save_grades(client, _get_upsert_payload(grade_context, date=date))
    _assert_error(res, 400, "date_required")


@pytest.mark.parametrize("date", ["not-a-date", "20240115", "2024-13-01", "2024-W03-1"])
def test_upsert_rejects_invalid_date(client, grade_context, date):
    login(client)
    res = _save_grades(client, _get_upsert_payload(grade_context, date=date))
    _assert_error(res, 400, "invalid_date_format")


@pytest.mark.parametrize("student_id", [None, 0])
def test_save_rejects_missing_student(client, student_id):
    login(client)
    res = _save_grades(client, {"student_id": student_id, "delete_grade_ids": [1]})
    _assert_error(res, 400, "student_id_required")


@pytest.mark.parametrize(
    "lists",
    [
        {},
        {"upsert_grades": [], "delete_grade_ids": []},
        {"upsert_grades": None, "delete_grade_ids": None},
    ],
)
def test_save_rejects_empty_payload(client, grade_context, lists):
    login(client)
    res = _save_grades(client, {"student_id": grade_context["student1_id"], **lists})
    _assert_error(res, 400, "grades_payload_required")


@pytest.mark.parametrize("student_key", ["teacher1_id", None])
def test_save_rejects_invalid_student(client, grade_context, student_key):
    login(client)
    student_id = grade_context[student_key] if student_key else MISSING_ID
    res = _save_grades(client, _get_delete_payload(grade_context, [1], student_id))
    _assert_error(res, 404, "not_found")


def test_upsert_rejects_non_object_entry(client, grade_context):
    login(client)
    # ** spreads the keys into one flat dict, the repeated upsert_grades key keeps its last value
    payload = {**_get_upsert_payload(grade_context), "upsert_grades": [8.0]}
    res = _save_grades(client, payload)
    _assert_error(res, 400, "invalid_payload")


@pytest.mark.parametrize("value", [True, False, "8.5", None])
def test_upsert_rejects_non_number_value(client, grade_context, value):
    login(client)
    res = _save_grades(client, _get_upsert_payload(grade_context, value))
    _assert_error(res, 400, "invalid_grade_value")


@pytest.mark.parametrize("value", [-0.1, 10.1, 11.0])
def test_upsert_rejects_value_out_of_range(client, grade_context, value):
    login(client)
    res = _save_grades(client, _get_upsert_payload(grade_context, value))
    _assert_error(res, 400, "grade_out_of_range")


def test_upsert_rejects_invalid_subcategory(client, grade_context):
    login(client)
    res = _save_grades(client, _get_upsert_payload(grade_context, subcategory_id=MISSING_ID))
    _assert_error(res, 400, "invalid_subcategory_id")


def test_upsert_rejects_duplicate_subcategory(client, grade_context):
    login(client)
    payload = _get_upsert_payload(grade_context, 3.0)
    payload["upsert_grades"].append({"subcategory_id": grade_context["subcategory1_id"], "value": 9.0})
    res = _save_grades(client, payload)
    _assert_error(res, 400, "duplicate_subcategory_id")
    assert _get_history(client, grade_context) == []


@pytest.mark.parametrize(
    "value, saved_value",
    [
        (8.5, 8.5),
        (0, 0),
        (10, 10),
        (7.46, 7.5),
    ],
)
def test_upsert_creates_grade(client, grade_context, value, saved_value):
    login(client)
    res = _save_grades(client, _get_upsert_payload(grade_context, value))
    _assert_saved(res)

    saved = _get_first_subcategory_grades(client, grade_context)[0]
    assert saved["value"] == saved_value
    assert saved["date"] == DEFAULT_DAY


def test_upsert_updates_existing_grade(client, grade_context):
    login(client)
    _assert_saved(_save_grades(client, _get_upsert_payload(grade_context, 8.5)))
    res = _save_grades(client, _get_upsert_payload(grade_context, 9.0))
    _assert_saved(res)

    # same student, subcategory and date: still one grade, with the new value
    assert [g["value"] for g in _get_first_subcategory_grades(client, grade_context)] == [9.0]


@pytest.mark.parametrize("grade_id", ["5", 5.0, True, None])
def test_delete_rejects_non_int_ids(client, grade_context, grade_id):
    login(client)
    res = _save_grades(client, _get_delete_payload(grade_context, [grade_id]))
    _assert_error(res, 400, "invalid_payload")


@pytest.mark.parametrize("include_existing", [False, True])
def test_delete_rejects_nonexistent_grade(client, grade_context, include_existing):
    login(client)
    grade_ids = [_create_grade(client, grade_context), MISSING_ID] if include_existing else [MISSING_ID]
    res = _save_grades(client, _get_delete_payload(grade_context, grade_ids))
    _assert_error(res, 404, "grades_not_found")


def test_delete_rejects_other_students_grade(client, grade_context):
    login(client)
    grade_id = _create_grade(client, grade_context)
    res = _save_grades(client, _get_delete_payload(grade_context, [grade_id], grade_context["student2_id"]))
    _assert_error(res, 400, "grades_wrong_student")


@pytest.mark.parametrize(
    "teacher, repeat",
    [
        ("teacher1", 1),
        ("teacher1", 2),  # sends same grade twice
        ("teacher2", 1),  # teacher2 deletes grade from teacher1
    ],
)
def test_delete_removes_grade(client, grade_context, teacher, repeat):
    login(client, "teacher1")
    grade_id = _create_grade(client, grade_context)
    login(client, teacher)
    res = _save_grades(client, _get_delete_payload(grade_context, [grade_id] * repeat))
    _assert_saved(res)
    assert _get_history(client, grade_context) == []


def test_save_upserts_and_deletes_together(client, grade_context):
    # one request deletes the subcategory1 grade of another day and creates a subcategory2 grade on DEFAULT_DAY
    _insert_grades(grade_context, ["2024-01-10"])
    login(client)
    grade_id = _get_day_grade_id(client, grade_context, "2024-01-10")
    payload = {
        **_get_upsert_payload(grade_context, 7.0, subcategory_id=grade_context["subcategory2_id"]),
        "delete_grade_ids": [grade_id],
    }
    _assert_saved(_save_grades(client, payload))

    subcategories = _get_history(client, grade_context)[0]["subcategories"]
    # the subcategory1 grade is deleted, only the new spin grade is left
    assert [s["name"] for s in subcategories] == ["spin"]
    assert [g["value"] for g in subcategories[0]["grades"]] == [7.0]


def test_upsert_by_other_teacher_takes_authorship(client, grade_context):
    login(client, "teacher1")
    _assert_saved(_save_grades(client, _get_upsert_payload(grade_context, 6.0)))
    login(client, "teacher2")
    _assert_saved(_save_grades(client, _get_upsert_payload(grade_context, 9.0)))

    # teacher_id is never sent to the frontend, so it is read from the db
    with get_session() as session:
        rows = session.execute(select(Grade.teacher_id, Grade.value)).all()
    assert rows == [(grade_context["teacher2_id"], 9.0)]


def test_day_grades_rejects_student_caller(client, grade_context):
    login(client, "student1")
    res = _get_day_grades(client, grade_context["student1_id"], DEFAULT_DAY)
    _assert_error(res, 403, "forbidden")


@pytest.mark.parametrize("date", ["not-a-date", "20240115"])
def test_day_grades_rejects_invalid_date(client, grade_context, date):
    login(client)
    res = _get_day_grades(client, grade_context["student1_id"], date)
    _assert_error(res, 400, "invalid_date_format")


@pytest.mark.parametrize("student_key", ["teacher1_id", None])
def test_day_grades_rejects_invalid_student(client, grade_context, student_key):
    login(client)
    student_id = grade_context[student_key] if student_key else MISSING_ID
    res = _get_day_grades(client, student_id, DEFAULT_DAY)
    _assert_error(res, 404, "not_found")


@pytest.mark.parametrize(
    "date, expected_count",
    [
        ("2024-01-15", 1),
        ("2024-01-16", 1),
        ("2024-01-17", 0),
    ],
)
def test_day_grades_returns_only_that_date(client, grade_context, date, expected_count):
    _insert_grades(grade_context, ["2024-01-15", "2024-01-16"])
    login(client)
    res = _get_day_grades(client, grade_context["student1_id"], date)
    assert res.status_code == 200
    body = res.get_json()
    assert len(body) == expected_count
    if expected_count:
        assert body[str(grade_context["subcategory1_id"])]["value"] == 5.0


def test_day_grades_ignores_history_limit(client, grade_context):
    dates = _make_daily_dates(200)
    _insert_grades(grade_context, dates)
    login(client)
    res = _get_day_grades(client, grade_context["student1_id"], dates[0])
    assert res.status_code == 200
    assert len(res.get_json()) == 1


def test_history_rejects_other_student(client, grade_context):
    login(client, "student1")
    res = client.get(f"/api/students/{grade_context['student2_id']}/grades")
    _assert_error(res, 403, "forbidden")


@pytest.mark.parametrize("student_key", ["teacher1_id", None])
def test_history_rejects_invalid_student(client, grade_context, student_key):
    login(client)
    student_id = grade_context[student_key] if student_key else MISSING_ID
    res = client.get(f"/api/students/{student_id}/grades")
    _assert_error(res, 404, "not_found")


@pytest.mark.parametrize(
    "query, expected_count",
    [
        ("?limit=5", 5),
        ("", 100),
        ("?limit=500", 100),
        ("?limit=abc", 100),
        ("?limit=0", 100),
        ("?limit=-1", 100),
    ],
)
def test_history_applies_limit(client, grade_context, query, expected_count):
    dates = _make_daily_dates(200)
    _insert_grades(grade_context, dates)
    login(client)
    grades = _get_first_subcategory_grades(client, grade_context, query)
    assert len(grades) == expected_count
    assert grades[-1]["date"] == dates[-1]


@pytest.mark.parametrize("username", ["student1", "teacher1"])
def test_history_returns_oldest_to_newest(client, grade_context, username):
    _insert_grades(grade_context, ["2024-01-20", "2024-01-05", "2024-01-12"])
    login(client, username)
    dates = [g["date"] for g in _get_first_subcategory_grades(client, grade_context)]
    assert dates == ["2024-01-05", "2024-01-12", "2024-01-20"]


def test_history_limits_each_subcategory(client, grade_context):
    # subcategory2 holds the newest dates: a global limit would take them first and cut subcategory1 to 2
    dates = _make_daily_dates(13)
    _insert_grades(grade_context, dates[:10])
    _insert_grades(grade_context, dates[10:], "subcategory2_id")
    login(client)
    subcategories = _get_history(client, grade_context, "?limit=5")[0]["subcategories"]
    assert [len(s["grades"]) for s in subcategories] == [5, 3]


def test_history_sorts_by_category_then_subcategory_id(client, grade_context):
    # dates run opposite to ids: query order alone would put smash first and spin before slice
    _insert_grades(grade_context, ["2024-01-01"], "subcategory3_id")
    _insert_grades(grade_context, ["2024-01-02"], "subcategory2_id")
    _insert_grades(grade_context, ["2024-01-03"])
    login(client)
    history = _get_history(client, grade_context)
    assert [c["category"] for c in history] == ["serve", "smash"]
    assert [s["name"] for s in history[0]["subcategories"]] == ["slice", "spin"]


def test_history_returns_nested_response(client, grade_context):
    # inserted across categories and newest first: nested by category, then subcategory, then oldest date
    _insert_grades(grade_context, ["2024-01-03"], "subcategory3_id")
    _insert_grades(grade_context, ["2024-01-02", "2024-01-01"], "subcategory2_id")
    _insert_grades(grade_context, ["2024-01-04", "2024-01-01"])

    def make_expected_subcategory(key, name, dates):
        grades = [{"value": 5.0, "date": date} for date in dates]
        return {"id": grade_context[key], "name": name, "grades": grades}

    login(client)
    assert _get_history(client, grade_context) == [
        {
            "category": "serve",
            "subcategories": [
                make_expected_subcategory("subcategory1_id", "slice", ["2024-01-01", "2024-01-04"]),
                make_expected_subcategory("subcategory2_id", "spin", ["2024-01-01", "2024-01-02"]),
            ],
        },
        {
            "category": "smash",
            "subcategories": [make_expected_subcategory("subcategory3_id", "angle", ["2024-01-03"])],
        },
    ]


def test_teacher_delete_removes_their_grades(client, grade_context):
    # teacher1 saves a grade, then admin deletes teacher1: the grade goes with them
    _insert_grades(grade_context, [DEFAULT_DAY])
    login(client, DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS)
    res = client.delete(f"/api/teachers/{grade_context['teacher1_id']}")
    assert res.status_code == 200
    login(client, "teacher2")
    assert _get_history(client, grade_context) == []


def test_save_rejects_other_arena_student(client, grade_context):
    other = _make_other_arena()
    login(client)
    payload = {**_get_upsert_payload(grade_context), "student_id": other["student_id"]}
    _assert_error(_save_grades(client, payload), 404, "not_found")


def test_upsert_rejects_other_arena_subcategory(client, grade_context):
    other = _make_other_arena()
    login(client)
    payload = _get_upsert_payload(grade_context, subcategory_id=other["subcategory_id"])
    _assert_error(_save_grades(client, payload), 400, "invalid_subcategory_id")


@pytest.mark.parametrize("path", ["grades", f"grades/{DEFAULT_DAY}"])
def test_reads_reject_other_arena_student(client, grade_context, path):
    other = _make_other_arena()
    login(client)
    _assert_error(client.get(f"/api/students/{other['student_id']}/{path}"), 404, "not_found")


def test_same_username_logs_into_its_own_arena(client, grade_context):
    _make_other_arena()
    login(client, arena=OTHER_ARENA)
    assert client.get("/api/me").get_json()["user"]["arena_name"] == OTHER_ARENA
    _assert_error(client.get(f"/api/students/{grade_context['student1_id']}/grades"), 404, "not_found")
