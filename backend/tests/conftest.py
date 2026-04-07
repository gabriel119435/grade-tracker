import os

# must be set before any app import so db.py picks it up at module load time
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# pytest discovers tests in files named test_*.py or *_test.py inside testpaths and runs functions named test_* inside them
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_session
from app.models import User, Category, Subcategory, Grade


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
    # fake http client: calls the flask app directly in-process, no tcp socket; routes and middleware run normally
    return app.test_client()


@pytest.fixture(autouse=True)
def grade_context(app):
    """creates two teachers, one student, one category, and one subcategory; cleans up all test data after each test"""
    with get_session(write=True) as session:
        p_hash = generate_password_hash('pass1234')
        teacher1 = User(username='teacher1', password_hash=p_hash, role='teacher')
        teacher2 = User(username='teacher2', password_hash=p_hash, role='teacher')
        student1 = User(username='student1', password_hash=p_hash, role='student')
        session.add_all([teacher1, teacher2, student1])
        session.flush()  # assigns ids before commit

        category1 = Category(name='serve')
        session.add(category1)
        session.flush()

        subcategory1 = Subcategory(name='slice', category_id=category1.id)
        session.add(subcategory1)
        session.flush()

        ids = {
            'teacher1_id': teacher1.id,
            'teacher2_id': teacher2.id,
            'student1_id': student1.id,
            'subcategory1_id': subcategory1.id,
            'password': 'pass1234',
        }

    yield ids

    with get_session(write=True) as session:
        session.query(Grade).delete()
        session.query(Subcategory).delete()
        session.query(Category).delete()
        session.query(User).filter(User.username != 'admin').delete()
