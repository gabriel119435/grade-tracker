from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import Arena, User
from app.validation import password_error, username_error


def create_arena(arena_name, admin_name, admin_pass):
    """
    creates an arena and its only admin in one transaction, both or neither.
    returns False when arena name is taken, raises: ValueError "<field>: <code>" on a bad value
    """
    errors = {
        "arena": _name_error(arena_name),
        "admin": _name_error(admin_name),
        "admin password": password_error(admin_pass),
    }
    for field, error in errors.items():
        if error:
            raise ValueError(f"{field}: {error}")

    try:
        with get_session(write=True) as session:
            arena = Arena(name=arena_name)
            session.add(arena)
            session.flush()
            session.add(
                User(
                    arena_id=arena.id,
                    username=admin_name,
                    password_hash=generate_password_hash(admin_pass),
                    role="admin",
                )
            )
    except IntegrityError:
        return False
    return True


def _name_error(name):
    return username_error(name) if name else "name_required"
