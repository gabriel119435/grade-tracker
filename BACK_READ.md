# backend reading order

a beginner's guide to the backend codebase, ordered from simple to complex.
each new file builds on what came before; read them in order for the most coherent picture.

- **entry point**
    - `pyproject.toml`: project name, python version, and dependencies
    - `run.py`: starts the flask dev server on port 5000
- **base**: database layer and wiring the application together
    - `db.py`: sqlite engine and `get_session()`; the single way to open a database session anywhere in the codebase
    - `models.py`: all database tables as python classes: `User`, `Category`, `Subcategory`, `Grade`, and `AuthUser`
    - `__init__.py`: `create_app()`; wires the database, auth, error handling, and all blueprints into a running flask
      app
- **route helpers**: shared utilities used by blueprints
    - `routes/helpers/annotations.py`: `require_role()` decorator; restricts an endpoint to specific logged in roles
    - `routes/helpers/users.py`: create and delete user methods; shared by both the teachers and students blueprints
- **routes**: one blueprint per resource
    - `routes/auth.py`: login, logout, session check, locale change, and admin password change
    - `routes/teachers.py`: list, create, and delete teacher accounts; admin only
    - `routes/students.py`: list, create, and delete student accounts; teacher only
    - `routes/categories.py`: manage categories and their subcategories; teacher only
    - `routes/grades.py`: save grades (upsert + delete in one request) and fetch a student's grade history
- **tests**: lives under `backend/tests/`, mirroring the `app/` structure
    - `tests/conftest.py`: pytest fixtures: creates the flask test client and some data for tests
    - `tests/routes/test_grades.py`: grade endpoint tests: upsert, update, delete, and ownership/validation rejections
- **dev tools**
    - `seed.py`: populates an empty database with test users, categories, subcategories, and a year of grades