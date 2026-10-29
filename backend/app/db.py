import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# backend/app/db.py -> backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app.db")


class Base(DeclarativeBase):
    pass


DB_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{DB_PATH}"

# journal_mode is sqlite's default delete: reads see the last commit during a write, a commit waits for open reads
# a wait longer than 5s (pysqlite default timeout) fails with "database is locked"

# conftest.py sets DATABASE_URL to sqlite:///:memory:
if DB_URL == "sqlite:///:memory:":
    from sqlalchemy.pool import StaticPool

    # in-memory sqlite is per connection: StaticPool shares one connection
    # used across threads, so the same-thread check is off
    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DB_URL)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    # enforce fk rules on db by default
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


@event.listens_for(engine, "checkin")
def reset_query_only(dbapi_conn, _):
    # every connection returns to the pool writable, whatever path released it
    # None when the connection was invalidated, nothing to reset
    if dbapi_conn is not None:
        dbapi_conn.execute("PRAGMA query_only = OFF")


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@contextmanager
def get_session(write=False):
    # plain sqlalchemy instead of flask-sqlalchemy, keeps sessions independent of the app context.
    # scripts, tests, and cli tools can open sessions without a running flask app
    session = SessionLocal()
    try:
        # read-only by default; pass write=True only when the session needs to commit changes
        if not write:
            session.execute(text("PRAGMA query_only = ON"))
        yield session
        if write:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
