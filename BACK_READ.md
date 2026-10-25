# backend reading order

a beginner's guide to the backend codebase, ordered from simple to complex.
each new file builds on what came before, read them in order for the most coherent picture.

- **entry point**
    - `pyproject.toml`: project name, python version, and dependencies
    - `.python-version`: exact python version uv installs and uses
    - `run.py`: starts the flask dev server on port 5000
- **base**: database layer and wiring the application together
    - `constants.py`: input length rules, supported locales and the default one mirrored by `frontend/src/constants.js`
    - `validation.py`: password, username, name length and word size checks built on those rules
    - `settings.py`: env vars for the first arena, its admin and the seed password, with fallbacks, checked on startup
    - `db.py`: sqlite engine and `get_session()`, the single way to open a database session anywhere in the codebase
    - `models.py`: tables `Arena`, `User`, `Category`, `Subcategory`, `Grade`, `AuthUser` and per arena `wipe()`
    - `migrations.py`: schema changes run on every startup, each one idempotent
    - `arena.py`: `create_arena()`, an arena and its only admin in one transaction, used by startup and cli
    - `__init__.py`: `create_app()`, wires the database, default arena, auth, errors and all blueprints into flask
- **route helpers**: shared utilities used by blueprints
    - `routes/helpers/decorators.py`: decorators for route access control
    - `routes/helpers/payload.py`: typed readers for json request fields, 400 on a wrong type
    - `routes/helpers/users.py`: user logic shared by the teacher and student routes, inside the caller's arena
- **routes**: one blueprint per resource
    - `routes/arenas.py`: public list of every arena
    - `routes/auth.py`: login per arena, logout, session check, locale change, and admin password change
    - `routes/teachers.py`: list, create, and delete teacher accounts, admin only
    - `routes/students.py`: list, create, and delete student accounts, teacher only
    - `routes/categories.py`: manage categories and their subcategories, teacher only
    - `routes/grades.py`: fetch and save grades (upsert + delete in one request)
    - `routes/seed.py`: wipes admin's arena except the admin user and fills it with seed data
- **cli**: run by hand next to the running app
    - `create_arena.py`: creates a new arena and its only admin, the only way to add an arena
- **tests**: live under `backend/tests/`, mirroring the `app/` structure
    - `tests/helpers.py`: plain functions and values shared by test files, like `login()`
    - `tests/conftest.py`: pytest fixtures: creates the flask test client and some data for tests
    - `tests/routes/test_grades.py`: grade endpoint tests