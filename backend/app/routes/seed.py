"""
wipes the db and fills it with beach tennis test data; admin only, triggered from the admin teachers screen.

wipe: deletes all grades, subcategories, categories and every user except 'admin'.
users: 5 teachers + 10 students, pass 'seed-pass', no first name or last name repeated across all 15 users.
categories: 10 hardcoded beach tennis shots, 50 hardcoded subcategories in total (3 to 8 per category).
grades: 5 rounds; each round picks a random teacher (may repeat) and a new random student (never repeats).
the 50 subcategories are shuffled and split for that student:
  20% (10 subcategories) -> 60 grades, one per day from day1 to day60
  20% (10 subcategories) -> 40 grades on random distinct days
  50% (25 subcategories) -> 20 grades on random distinct days
  10% (5 subcategories)  -> no grades
values are random 0.0 to 10.0; the other 5 students get no grades.
everything runs in one transaction: any error rolls back the wipe too.
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

SEED_PASS = "seed-pass"
TEACHER_COUNT = 5
STUDENT_COUNT = 10
GRADED_STUDENT_COUNT = 5

# 10 male + 10 female first names, 20 last names; pt-br spelling
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
    "forehand": ["força", "precisão", "consistência", "profundidade", "mobilidade", "técnica", "efeito"],
    "backhand": ["força", "precisão", "consistência", "mobilidade", "técnica", "profundidade"],
    "saque": ["força", "precisão", "efeito", "consistência", "colocação"],
    "recepção": ["posicionamento", "reflexo", "precisão", "mobilidade", "inteligência"],
    "curta": ["precisão", "disfarce", "inteligência"],
    "smash": ["força", "velocidade", "timing", "colocação", "salto", "finalização"],
    "lob": ["altura", "profundidade", "disfarce", "inteligência"],
    "gancho": ["timing", "mobilidade", "técnica"],
    "voleio": ["reflexo", "precisão", "posicionamento", "velocidade", "mobilidade", "consistência", "inteligência",
               "timing"],
    "verônica": ["timing", "técnica", "colocação"],
}

DAY1 = date(2025, 5, 25)
DAY_COUNT = 60  # day1 to day60 inclusive, day60 = 2025-07-23

# (percentage of subcats, grades per subcat); last tier takes whatever is left and gets no grades
GRADE_TIERS = [(20, 60), (20, 40), (50, 20), (10, 0)]


@seed_bp.route("/api/admin/seed", methods=["POST"])
@require_role("admin")
def seed():
    return jsonify(run_seed())


def run_seed():
    """
    wipes the db, keeping only the admin user, then creates users, categories, subcategories and grades.
    returns: dict counts of created rows, keys teachers, students, categories, subcategories, grades.
    """
    with get_session(write=True) as session:
        _wipe(session)
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


def _wipe(session):
    """
    deletes all grades, subcategories, categories and non admin users, children first.
    session: Session open write session.
    """
    session.execute(delete(Grade))
    session.execute(delete(Subcategory))
    session.execute(delete(Category))
    session.execute(delete(User).where(User.username != "admin"))


def _create_users(session):
    """
    creates teachers and students with random unique names, all sharing SEED_PASS.
    session: Session open write session.
    returns: tuple[list[int], list[int]] teacher ids and student ids.
    """
    # one hash for everyone: same password, and hashing is slow on purpose
    password_hash = generate_password_hash(SEED_PASS)
    names = _random_names(TEACHER_COUNT + STUDENT_COUNT)

    teachers = [
        User(username=n, password_hash=password_hash, role="teacher", locale="pt-br") for n in names[:TEACHER_COUNT]
    ]
    students = [
        User(username=n, password_hash=password_hash, role="student", locale="pt-br") for n in names[TEACHER_COUNT:]
    ]
    session.add_all(teachers + students)
    session.flush()  # assigns ids

    return [t.id for t in teachers], [s.id for s in students]


def _random_names(count):
    """
    builds unique 'first last' names; no first name or last name is used twice.
    count: int number of names to build, max len(FIRST_NAMES).
    returns: list[str] names like 'maria silva'.
    """
    firsts = random.sample(FIRST_NAMES, count)
    lasts = random.sample(LAST_NAMES, count)
    return [f"{first} {last}" for first, last in zip(firsts, lasts)]


def _create_categories(session):
    """
    creates every category in CATEGORIES with its subcategories.
    session: Session open write session.
    returns: list[int] ids of all created subcategories.
    """
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
    """
    gives grades to GRADED_STUDENT_COUNT distinct students, each from a random teacher, following GRADE_TIERS.
    session: Session open write session.
    teacher_ids: list[int] teachers to pick from, repeats allowed.
    student_ids: list[int] students to pick from, no repeats.
    subcat_ids: list[int] subcategories to spread grades over.
    returns: int number of grades inserted.
    """
    all_days = [(DAY1 + timedelta(days=d)).isoformat() for d in range(DAY_COUNT)]
    sizes = _tier_sizes(len(subcat_ids))
    rows = []

    for student_id in random.sample(student_ids, GRADED_STUDENT_COUNT):
        teacher_id = random.choice(teacher_ids)
        shuffled = random.sample(subcat_ids, len(subcat_ids))

        start = 0
        for size, (_, grade_count) in zip(sizes, GRADE_TIERS):
            for subcat_id in shuffled[start:start + size]:
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
    """
    converts GRADE_TIERS percentages into subcat counts; the last tier takes the rounding leftover.
    subcat_count: int total number of subcategories.
    returns: list[int] subcategories per tier, same order as GRADE_TIERS.
    """
    sizes = [subcat_count * pct // 100 for pct, _ in GRADE_TIERS[:-1]]
    sizes.append(subcat_count - sum(sizes))
    return sizes
