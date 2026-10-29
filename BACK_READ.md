# backend reading order

a beginner's guide to the backend codebase, ordered from simple to complex.
each new file builds on what came before, read them in order for the most coherent picture.

- **entry point**
    - `pyproject.toml`: project name, python version and dependencies.
    - `.python-version`: pins the python version uv uses.
    - `run.py`: starts the flask dev server on port 5000.
- **base**: database layer and wiring the application together, under `app/`
    - `constants.py`: length rules and locales, mirrored by `frontend/src/constants.js`.
    - `validation.py`: password, username and name checks built on those rules.
    - `settings.py`: env vars for the first arena, its admin and the seed password, with fallbacks, checked on startup.
    - `db.py`: engine and `get_session()`, the only session entry point, migrations use the engine directly.
    - `models.py`: every table as a python class, plus `AuthUser` and per arena `wipe()`.
    - `migrations.py`: idempotent schema changes, run on every startup.
    - `arena.py`: `create_arena()`, an arena and its only admin in one transaction.
    - `seed_data.py`: demo names and beach tennis categories for `routes/seed.py`.
    - `__init__.py`: `create_app()`: logging, migrations, default arena, cookie policy, auth, errors, blueprints.
- **route helpers**: shared utilities used by blueprints, under `app/routes/helpers/`
    - `decorators.py`: `require_role()`, 401 when logged out, 403 for another role.
    - `payload.py`: typed readers for json request fields, 400 on a wrong type.
    - `scope.py`: `get_in_arena()`, a row of the caller's arena, 404 otherwise.
    - `users.py`: list, create and delete users of one role, shared by teachers and students.
- **routes**: one blueprint per resource, under `app/routes/`
    - `arenas.py`: public arena list for the login picker.
    - `auth.py`: login per arena, logout, session check, locale, admin password.
    - `teachers.py`: list, create and delete teachers, admin only.
    - `students.py`: list, create and delete students, teacher only.
    - `categories.py`: categories and subcategories, teacher only.
    - `grades.py`: save grades (upsert and delete in one request), one day's grades, history.
    - `seed.py`: wipes the admin's arena except the admin, fills it with demo data.
- **tests**: mirroring the `app/` structure, under `tests/`
    - `helpers.py`: plain values and functions shared by tests, like `login()`.
    - `conftest.py`: fixtures: app, client, 2 teachers, 2 students, 2 categories, cleanup.
    - `routes/test_grades.py`: grade endpoints, validation, limits, ordering, cross-arena isolation.
- **dev tools**
    - `create_arena.py`: creates a new arena and its only admin, the only way to add one, run by hand.
