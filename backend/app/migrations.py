from sqlalchemy import text

from app.constants import DEFAULT_LOCALE
from app.db import Base, engine


# migrations are by default idempotent, are always applied on startup
def apply_migrations():
    _migration_000_create_db()
    _migration_001_add_locale()


def _migration_000_create_db():
    Base.metadata.create_all(engine)  # idempotent: no op if tables already exist


def _migration_001_add_locale():
    with engine.connect() as conn:
        # runs after 000, so the users table always exists here
        columns = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
        if "locale" not in columns:
            conn.execute(text(f"ALTER TABLE users ADD COLUMN locale TEXT NOT NULL DEFAULT '{DEFAULT_LOCALE}'"))
            conn.commit()
