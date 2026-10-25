import os

from app.validation import password_error, username_error

# values read once from env vars at import. the fallbacks are known weak defaults for local dev only
# arena name, admin name and admin password are only used on a startup with no arena
DEFAULT_ARENA_NAME = os.environ.get("DEFAULT_ARENA_NAME") or "arena de teste"
DEFAULT_ADMIN_NAME = os.environ.get("DEFAULT_ADMIN_NAME") or "administrador"
DEFAULT_ADMIN_PASS = os.environ.get("DEFAULT_ADMIN_PASS") or "senha primaria"
DEFAULT_SEED_PASS = os.environ.get("DEFAULT_SEED_PASS") or "senha secundaria"


def check_settings():
    # same rules as every other username and password, for both the env value and the fallback
    # runs on startup, so a bad value stops the app instead of failing on first admin creation or first seed
    errors = {
        "DEFAULT_ARENA_NAME": username_error(DEFAULT_ARENA_NAME),
        "DEFAULT_ADMIN_NAME": username_error(DEFAULT_ADMIN_NAME),
        "DEFAULT_ADMIN_PASS": password_error(DEFAULT_ADMIN_PASS),
        "DEFAULT_SEED_PASS": password_error(DEFAULT_SEED_PASS),
    }
    for var, error in errors.items():
        if error:
            raise ValueError(f"{var}: {error}")
