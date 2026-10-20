# backend reading order

a beginner's guide to the backend codebase, ordered from simple to complex.
each new file builds on what came before, read them in order for the most coherent picture.

- **entry point**
    - `pyproject.toml`: project name, python version, and dependencies
    - `.python-version`: exact python version uv installs and uses
    - `run.py`: starts the flask dev server on port 5000
- **base**: database layer and wiring the application together
    - `constants.py`: input length rules, supported locales and the default one mirrored by `frontend/src/constants.js`
    - `validation.py`: password length, name length and word size checks built on those rules
    - `db.py`: sqlite engine and `get_session()`, the single way to open a database session anywhere in the codebase
    - `models.py`: tables `User`, `Category`, `Subcategory`, `Grade`, plus `AuthUser` and `wipe()` keeping only admin
    - `migrations.py`: schema changes run on every startup, each one idempotent
    - `__init__.py`: `create_app()`, wires the database, auth, error handling, and all blueprints into a flask app
- **route helpers**: shared utilities used by blueprints
    - `routes/helpers/decorators.py`: decorators for route access control
    - `routes/helpers/payload.py`: typed readers for json request fields, 400 on a wrong type
    - `routes/helpers/users.py`: user logic shared by the teacher and student routes
- **routes**: one blueprint per resource
    - `routes/auth.py`: login, logout, session check, locale change, and admin password change
    - `routes/teachers.py`: list, create, and delete teacher accounts, admin only
    - `routes/students.py`: list, create, and delete student accounts, teacher only
    - `routes/categories.py`: manage categories and their subcategories, teacher only
    - `routes/grades.py`: fetch and save grades (upsert + delete in one request)
    - `routes/seed.py`: wipes the database except the admin user and fills it with beach tennis data
- **tests**: live under `backend/tests/`, mirroring the `app/` structure
    - `tests/helpers.py`: plain functions and values shared by test files, like `login()`
    - `tests/conftest.py`: pytest fixtures: creates the flask test client and some data for tests
    - `tests/routes/test_grades.py`: grade endpoint tests