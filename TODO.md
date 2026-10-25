# pending/future tasks

## pending

## future

- stale tab writes issue: a tab left open across another tab's login writes as the new user
    - locale switch saves into the new user's account, a same-role teacher saves grades under the new `teacher_id`
- cache `load_user`: it runs a full `SELECT` on every authenticated request; worth it if traffic grows.
- backend files with no tests:
    - `validation.py`, `settings.py`, `db.py`, `arena.py`, `app/__init__.py`, `decorators.py`, `payload.py`, `users.py`
    - `arenas.py`, `auth.py`, `teachers.py`, `students.py`, `categories.py`, `seed.py`, `create_arena.py`
- frontend files with no tests:
    - `request.js`, `translateError.js`, `clickOutside.js`, `i18n.js`, `en.js`, `pt-br.js`, `constants.js`
    - `composables/`, `components/`, `layouts/` and `views/`