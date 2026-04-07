import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# backend/app/db.py -> backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app.db")


class Base(DeclarativeBase):
    pass


DB_URL = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')

# conftest.py sets DATABASE_URL to sqlite:///:memory:
if DB_URL == 'sqlite:///:memory:':
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        DB_URL,
        # prod uses one connection per request (same thread), StaticPool shares one connection across sessions, which can cross threads
        connect_args={'check_same_thread': False},
        # in-memory sqlite is per-connection, not shared ram, StaticPool reuses one connection so fixture data is visible to every test
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DB_URL)


# enforce fk rules on db by default
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


@contextmanager
def get_session(write=False):
    # plain sqlalchemy instead of flask-sqlalchemy, keeps sessions independent of the app
    # context so scripts, tests, and CLI tools can open sessions without a running flask app
    # read-only by default; pass write=True only when the session needs to commit changes
    session = SessionLocal()
    try:
        if not write:
            session.execute(text("PRAGMA query_only = ON"))
        yield session
        if write:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        if not write:
            session.execute(text("PRAGMA query_only = OFF"))
        session.close()
