"""
admin only: wipes admin's own arena except the admin user, then adds beach tennis demo data, in one transaction.
- users: 5 teachers, 10 students, password DEFAULT_SEED_PASS from settings.py, no first or last name repeated.
- categories: 10 shots, 44 subcategories (2 to 6 each).
- grades: 5 students, one random teacher each, values 0.0 to 10.0. shuffled subcategories split in tiers:
  20% -> 60 grades (one per day), 20% -> 40, 50% -> 20 (random distinct days), 10% -> none.
"""

import random
from datetime import date, timedelta

from flask import Blueprint, jsonify
from flask_login import current_user
from sqlalchemy import insert
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import Category, Grade, Subcategory, User, wipe
from app.routes.helpers.decorators import require_role
from app.seed_data import CATEGORIES, FIRST_NAMES, LAST_NAMES
from app.settings import DEFAULT_SEED_PASS

seed_bp = Blueprint("seed", __name__)

TEACHER_COUNT = 5
STUDENT_COUNT = 10
GRADED_STUDENT_COUNT = 5

DAY1 = date(2025, 5, 25)
DAY_COUNT = 60

# (percentage of subcats, grades per subcat)
GRADE_TIERS = [(20, 60), (20, 40), (50, 20), (10, 0)]


# enabled in every environment
@seed_bp.route("/api/admin/seed", methods=["POST"])
@require_role("admin")
def seed():
    return jsonify(run_seed(current_user.arena_id))


def run_seed(arena_id):
    """
    wipes one arena, keeping its admin user, then creates its users, categories, subcategories and grades.
    other arenas are never touched.
    arena_id: int the arena to wipe and fill.
    returns counts of created rows, keys teachers, students, categories, subcategories, grades.
    """
    with get_session(write=True) as session:
        wipe(session, arena_id)
        teacher_ids, student_ids = _create_users(session, arena_id)
        subcat_ids = _create_categories(session, arena_id)
        grade_count = _create_grades(session, teacher_ids, student_ids, subcat_ids)

    return {
        "teachers": len(teacher_ids),
        "students": len(student_ids),
        "categories": len(CATEGORIES),
        "subcategories": len(subcat_ids),
        "grades": grade_count,
    }


def _create_users(session, arena_id):
    # creates the arena's teachers and students with random unique names, all sharing the seed password.
    password_hash = generate_password_hash(DEFAULT_SEED_PASS)
    names = _random_names(TEACHER_COUNT + STUDENT_COUNT)

    def make(name, role):
        return User(arena_id=arena_id, username=name, password_hash=password_hash, role=role)

    teachers = [make(n, "teacher") for n in names[:TEACHER_COUNT]]
    students = [make(n, "student") for n in names[TEACHER_COUNT:]]
    session.add_all(teachers + students)
    session.flush()  # assigns ids

    return [t.id for t in teachers], [s.id for s in students]


def _random_names(count):
    # builds unique 'first last' names
    firsts = random.sample(FIRST_NAMES, count)
    lasts = random.sample(LAST_NAMES, count)
    return [f"{first} {last}" for first, last in zip(firsts, lasts)]


def _create_categories(session, arena_id):
    # creates every cat in CATEGORIES with its subcats in the arena.
    subcategories = []
    for cat_name, subcat_names in CATEGORIES.items():
        cat = Category(name=cat_name, arena_id=arena_id)
        session.add(cat)
        session.flush()  # assigns cat.id

        for subcat_name in subcat_names:
            subcategories.append(Subcategory(name=subcat_name, category_id=cat.id))

    session.add_all(subcategories)
    session.flush()
    return [s.id for s in subcategories]


def _create_grades(session, teacher_ids, student_ids, subcat_ids):
    # gives grades to GRADED_STUDENT_COUNT distinct students, each from a random teacher, following GRADE_TIERS.
    all_days = [(DAY1 + timedelta(days=d)).isoformat() for d in range(DAY_COUNT)]
    sizes = _tier_sizes(len(subcat_ids))
    rows = []

    # GRADED_STUDENT_COUNT distinct students get grades, the rest get none
    for student_id in random.sample(student_ids, GRADED_STUDENT_COUNT):
        # the same teacher may be picked for several students
        teacher_id = random.choice(teacher_ids)
        shuffled_subcat_ids = random.sample(subcat_ids, len(subcat_ids))

        start = 0
        for size, (_, grade_count) in zip(sizes, GRADE_TIERS):
            for subcat_id in shuffled_subcat_ids[start : start + size]:
                # distinct days: one grade per student per subcat per day is a unique constraint
                for day in random.sample(all_days, grade_count):
                    rows.append(
                        {
                            "value": round(random.uniform(0, 10), 1),
                            "date": day,
                            "student_id": student_id,
                            "teacher_id": teacher_id,
                            "subcategory_id": subcat_id,
                        }
                    )
            start += size

    session.execute(insert(Grade), rows)
    return len(rows)


def _tier_sizes(subcat_count):
    # converts GRADE_TIERS percentages into subcat counts
    sizes = [subcat_count * pct // 100 for pct, _ in GRADE_TIERS[:-1]]
    sizes.append(subcat_count - sum(sizes))
    return sizes
