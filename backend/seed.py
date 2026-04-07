#!/usr/bin/env python3
"""
populates the db with test users, categories, and grades.

teachers : t12345678-1 ... t12345678-10  (pass = username)
           9000...0  (9 + 24 zeros)      (pass = username)
students : s12345678-1 ... s12345678-10  (pass = username)
           0000...9  (24 zeros + 9)      (pass = username)
categories:
  - "0"*25  -> 11 subcats: "0"*25, cat1 ... cat10
  - cat1 ... cat10 → random 0–10 subcats each (guaranteed: ≥2 cats with 10 subcats, ≥2 cats with 0 subcats)
grades (teacher 9000...0):
  - students: 000...09 + 2 random numbered students
  - categories: "0"*25 + 2 random other cats that have subcats
  - per (student, category): 365 grades on random dates from the last 730 days,
    one grade per subcategory per date

usage: uv run seed.py
no running server needed, connects to the sqlite db directly.
"""

import os
import random
import sys
from datetime import date, timedelta

# adds backend/ to import search path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import func, insert, select
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import Category, Grade, Subcategory, User

ZEROS = "0" * 25


def _abort_if_db_not_empty():
    with get_session() as session:
        counts = {
            "users": session.scalar(select(func.count()).select_from(User)),
            "categories": session.scalar(select(func.count()).select_from(Category)),
            "subcategories": session.scalar(select(func.count()).select_from(Subcategory)),
            "grades": session.scalar(select(func.count()).select_from(Grade)),
        }
    if any(counts.values()):
        print(f"db not empty: {counts}")
        sys.exit(1)


def _make_user(username, role):
    return User(username=username, password_hash=generate_password_hash(username), role=role, locale="en")


def _create_teachers(session):
    numbered = []
    # includes 1 excludes 11, 10 values
    for i in range(1, 11):
        name = f"t12345678-{i}"
        session.add(_make_user(name, "teacher"))
        numbered.append(name)

    special = _make_user("9" + "0" * 24, "teacher")
    session.add(special)
    return numbered, special


def _create_students(session):
    numbered = []
    for i in range(1, 11):
        u = _make_user(f"s12345678-{i}", "student")
        session.add(u)
        numbered.append(u)

    special = _make_user("0" * 24 + "9", "student")
    session.add(special)
    return numbered, special


def _create_category_zeros(session):
    cat = Category(name=ZEROS)
    session.add(cat)
    session.flush()

    subcats = []
    # ["0...0", "cat1", "cat2", ..., "cat10"]
    for name in [ZEROS] + [f"cat{i}" for i in range(1, 11)]:
        sub = Subcategory(name=name, category_id=cat.id)
        session.add(sub)
        subcats.append(sub)
    session.flush()

    return cat, [s.id for s in subcats]


def _generate_subcat_counts():
    # start with 10 random counts, then enforce boundary coverage:
    # at least 2 categories must have exactly 10 subcats (max boundary)
    # at least 2 categories must have exactly 0 subcats (empty boundary)
    subcats_per_cat = [random.randint(0, 10) for _ in range(10)]

    tens = [i for i, c in enumerate(subcats_per_cat) if c == 10]
    if len(tens) < 2:
        # only promote entries that are not already 0, avoid turning an empty cat into a full one
        eligible = [i for i, c in enumerate(subcats_per_cat) if c != 0]
        for i in random.sample(eligible, 2 - len(tens)):
            subcats_per_cat[i] = 10

    zeros = [i for i, c in enumerate(subcats_per_cat) if c == 0]
    if len(zeros) < 2:
        # only demote entries that are not already 10, avoid undoing the guarantee above
        eligible = [i for i, c in enumerate(subcats_per_cat) if c != 10]
        for i in random.sample(eligible, 2 - len(zeros)):
            subcats_per_cat[i] = 0

    return subcats_per_cat


def _create_other_categories(session, subcats_per_cat):
    cats = []
    for i, count in enumerate(subcats_per_cat):
        cat = Category(name=f"cat{i + 1}")
        session.add(cat)
        session.flush()

        subcats = []
        for j in range(1, count + 1):
            sub = Subcategory(name=f"subcat{j}", category_id=cat.id)
            session.add(sub)
            subcats.append(sub)
        if subcats:
            session.flush()

        cats.append((cat, [s.id for s in subcats]))
    return cats


def _insert_grades(session, teacher_id, student_ids, grade_cats):
    today = date.today()
    date_pool = [(today - timedelta(days=d)).isoformat() for d in range(730)]

    grade_insert = insert(Grade)
    inserted = 0

    for student_id in student_ids:
        for _cat, subcat_ids in grade_cats:
            chosen_dates = random.sample(date_pool, 365)
            grade_rows = [
                {"value": round(random.uniform(0, 10), 1), "date": chosen_date,
                 "student_id": student_id, "teacher_id": teacher_id, "subcategory_id": subcat_id}
                for chosen_date in chosen_dates
                for subcat_id in subcat_ids
            ]
            session.execute(grade_insert, grade_rows)
            inserted += len(grade_rows)

    return inserted


_abort_if_db_not_empty()

with get_session(write=True) as session:
    _numbered_teachers, t_special = _create_teachers(session)
    numbered_students, s_special = _create_students(session)
    session.flush() # pushes pending sql to db within the current transaction, assigns auto-generated ids during flush

    cat_zeros, cat_zeros_subcat_ids = _create_category_zeros(session)

    # simple array of ints, showing how much subcats each cat has
    subcats_per_cat = _generate_subcat_counts()
    # returns a list of tuples, where each tuple is (Category, list[int])
    other_cats = _create_other_categories(session, subcats_per_cat)

    grade_students = [s_special] + random.sample(numbered_students, 2)
    grade_cats = [(cat_zeros, cat_zeros_subcat_ids)] + random.sample(
        [(cat, sub_cat_ids) for cat, sub_cat_ids in other_cats if sub_cat_ids], 2
    )

    inserted = _insert_grades(session, t_special.id, [s.id for s in grade_students], grade_cats)

print(f"{inserted} grades inserted")
