import os

# must be set before any app import so db.py picks it up at module load time
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_session
from app.models import User, Category, Subcategory
from app.routes.seed import wipe
from tests.helpers import PASSWORD


# session is the entire test runtime, so once per test run
@pytest.fixture(scope='session')
def app():
    app = create_app()
    # makes flask propagate exceptions instead of catching them into 500 responses, so pytest shows the real traceback
    app.config['TESTING'] = True
    return app


# function-scoped so each test starts unauthenticated with a clean cookie jar
@pytest.fixture
def client(app):
    # fake http client: calls the flask app directly in-process, no tcp socket. routes and middleware run normally
    return app.test_client()


@pytest.fixture(autouse=True)
def grade_context(app):
    # creates two teachers, two students, two categories and three subcategories, wipes all test data after each test
    with get_session(write=True) as session:
        p_hash = generate_password_hash(PASSWORD)
        teacher1 = User(username='teacher1', password_hash=p_hash, role='teacher')
        teacher2 = User(username='teacher2', password_hash=p_hash, role='teacher')
        student1 = User(username='student1', password_hash=p_hash, role='student')
        student2 = User(username='student2', password_hash=p_hash, role='student')
        session.add_all([teacher1, teacher2, student1, student2])
        session.flush()  # assigns ids before commit

        category1 = Category(name='serve')
        category2 = Category(name='smash')
        session.add_all([category1, category2])
        session.flush()

        # two subcategories in category1 and one in category2, for limit and ordering tests
        subcategory1 = Subcategory(name='slice', category_id=category1.id)
        subcategory2 = Subcategory(name='spin', category_id=category1.id)
        subcategory3 = Subcategory(name='angle', category_id=category2.id)
        session.add_all([subcategory1, subcategory2, subcategory3])
        session.flush()

        ids = {
            'teacher1_id': teacher1.id,
            'teacher2_id': teacher2.id,
            'student1_id': student1.id,
            'student2_id': student2.id,
            'subcategory1_id': subcategory1.id,
            'subcategory2_id': subcategory2.id,
            'subcategory3_id': subcategory3.id,
        }

    yield ids

    with get_session(write=True) as session:
        wipe(session)
