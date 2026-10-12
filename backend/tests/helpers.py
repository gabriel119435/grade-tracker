# plain functions and values shared by test files, fixtures live in conftest.py

# password of every user created by the grade_context fixture
PASSWORD = 'pass1234'
# default admin password from app/__init__.py, used while ADMIN_PASS is unset
ADMIN_PASSWORD = 'admin pass'


def login(client, username='teacher1', password=PASSWORD):
    res = client.post('/api/login', json={'username': username, 'password': password})
    assert res.status_code == 200, f'login failed for {username}'
