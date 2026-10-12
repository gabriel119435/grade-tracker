"""
admin only: wipes everything except user 'admin', then adds beach tennis demo data, in one transaction.
- users: 5 teachers, 10 students, password 'seed pass', no first or last name repeated.
- categories: 10 shots, 50 subcategories (3 to 7 each).
- grades: 5 students, one random teacher each, values 0.0 to 10.0. shuffled subcategories split in tiers:
  20% -> 60 grades (one per day), 20% -> 40, 50% -> 20 (random distinct days), 10% -> none.
"""

import random
from datetime import date, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import delete, insert
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import Category, Grade, Subcategory, User
from app.routes.helpers.decorators import require_role

seed_bp = Blueprint("seed", __name__)

SEED_PASS = "seed pass"
TEACHER_COUNT = 5
STUDENT_COUNT = 10
GRADED_STUDENT_COUNT = 5

# 10 male + 10 female first names, 20 last names, pt-br spelling
FIRST_NAMES = [
    # male
    "josé", "joão", "antônio", "francisco", "pedro", "carlos", "lucas", "luiz", "paulo", "gabriel",
    # female
    "maria", "ana", "francisca", "júlia", "antônia", "juliana", "adriana", "fernanda", "márcia", "patrícia",
]
LAST_NAMES = [
    "silva", "santos", "oliveira", "souza", "pereira", "ferreira", "lima", "alves", "rodrigues", "costa",
    "sousa", "gomes", "nascimento", "araújo", "ribeiro", "almeida", "jesus", "barbosa", "soares", "carvalho",
]

# category -> subcategories, 50 subcats in total so the grade tier percentages split evenly
CATEGORIES = {
    "saque": ["chapado", "com slice", "com topspin", "curto", "por baixo", "no corpo"],
    "recepção": ["de voleio", "bloqueada", "em lob", "curta", "agressiva"],
    "forehand": ["cruzado", "paralelo", "acelerado", "com topspin", "de defesa", "na meia altura"],
    "backhand": ["cruzado", "paralelo", "bloqueio", "cortado", "de defesa", "na meia altura"],
    "voleio": ["de forehand", "de backhand", "alto", "baixo", "de toque", "angulado", "de bloqueio"],
    "smash": ["chapado", "com efeito", "diagonal", "defensivo", "de fundo"],
    "lob": ["defensivo", "ofensivo", "alto", "curto", "cruzado"],
    "gancho": ["na rede", "de fundo", "angulado"],
    "verônica": ["na rede", "de fundo", "angulado"],
    "curta": ["de forehand", "de backhand", "de voleio", "cruzada"],
}

DAY1 = date(2025, 5, 25)
DAY_COUNT = 60

# (percentage of subcats, grades per subcat)
GRADE_TIERS = [(20, 60), (20, 40), (50, 20), (10, 0)]


# enabled in every environment
@seed_bp.route("/api/admin/seed", methods=["POST"])
@require_role("admin")
def seed():
    return jsonify(run_seed())


def run_seed():
    """
    wipes the db, keeping only the admin user, then creates users, categories, subcategories and grades.
    returns counts of created rows, keys teachers, students, categories, subcategories, grades.
    """
    with get_session(write=True) as session:
        wipe(session)
        teacher_ids, student_ids = _create_users(session)
        subcat_ids = _create_categories(session)
        grade_count = _create_grades(session, teacher_ids, student_ids, subcat_ids)

    return {
        "teachers": len(teacher_ids),
        "students": len(student_ids),
        "categories": len(CATEGORIES),
        "subcategories": len(subcat_ids),
        "grades": grade_count,
    }


def wipe(session):
    # deletes all grades, subcategories, categories and non admin users, children first.
    session.execute(delete(Grade))
    session.execute(delete(Subcategory))
    session.execute(delete(Category))
    session.execute(delete(User).where(User.username != "admin"))


def _create_users(session):
    # creates teachers and students with random unique names, all sharing SEED_PASS.
    password_hash = generate_password_hash(SEED_PASS)
    names = _random_names(TEACHER_COUNT + STUDENT_COUNT)

    teachers = [
        User(username=n, password_hash=password_hash, role="teacher") for n in names[:TEACHER_COUNT]
    ]
    students = [
        User(username=n, password_hash=password_hash, role="student") for n in names[TEACHER_COUNT:]
    ]
    session.add_all(teachers + students)
    session.flush()  # assigns ids

    return [t.id for t in teachers], [s.id for s in students]


def _random_names(count):
    # builds unique 'first last' names
    firsts = random.sample(FIRST_NAMES, count)
    lasts = random.sample(LAST_NAMES, count)
    return [f"{first} {last}" for first, last in zip(firsts, lasts)]


def _create_categories(session):
    # creates every cat in CATEGORIES with its subcats.
    subcategories = []
    for cat_name, subcat_names in CATEGORIES.items():
        cat = Category(name=cat_name)
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
            for subcat_id in shuffled_subcat_ids[start:start + size]:
                # distinct days: one grade per student per subcat per day is a unique constraint
                for day in random.sample(all_days, grade_count):
                    rows.append(
                        {
                            "value": round(random.uniform(0, 10), 1),
                            "date": day,
                            "student_id": student_id,
                            "teacher_id": teacher_id,
                            "subcategory_id": subcat_id
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
