# pending/future tasks

## pending

## future

- stale tab writes issue: a tab left open across another tab's login writes as the new user
    - locale switch saves into the new user's account; same-role teacher saves grades under the new `teacher_id`
- cache `load_user`: it runs a full `SELECT` on every authenticated request; worth it if traffic grows.
- backend files with no tests:
    - `run.py`, `constants.py`, `validation.py`, `settings.py`, `db.py`, `models.py`
    - `migrations.py`, `arena.py`, `seed_data.py`, `app/__init__.py`
    - `decorators.py`, `payload.py`, `scope.py`, `users.py`
    - `arenas.py`, `auth.py`, `teachers.py`, `students.py`, `categories.py`, `seed.py`, `create_arena.py`
- frontend files with no tests:
    - `main.js`, `constants.js`, `en.js`, `pt-br.js`, `i18n.js`, `translateError.js`
    - `store.js`, `request.js`, `App.vue`, `clickOutside.js`
    - `composables/`, `api/routes/`, `components/`, `layouts/` and `views/`