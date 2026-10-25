# plain functions and values shared by test files, fixtures live in conftest.py
from sqlalchemy import select

from app.db import get_session
from app.models import Arena
from app.settings import DEFAULT_ARENA_NAME

# password of every user created by the grade_context fixture
PASSWORD = "pass1234"


def login(client, username="teacher1", password=PASSWORD, arena=DEFAULT_ARENA_NAME):
    with get_session() as session:
        arena_id = session.scalar(select(Arena.id).filter_by(name=arena))
    res = client.post("/api/login", json={"arena_id": arena_id, "username": username, "password": password})
    assert res.status_code == 200, f"login failed for {username}"
