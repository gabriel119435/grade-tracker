# pending/future tasks

## pending

- cloudflare tunnel deploy, both before the first deploy, per-ip limits (login included) need the real visitor ip:
    - `nginx.conf`: replace `CLOUDFLARED_IP` in the disabled realip lines above `location /api/` and uncomment them
    - `.env`: set `SESSION_COOKIE_SECURE=1`, session cookie only travels over https

## future

- arenas: tie teachers and students to arenas; today all teachers share every student, category and grade.
- cache `load_user`: it runs a full `SELECT` on every authenticated request; worth it if traffic grows.
- backend files with no tests:
    - `app/__init__.py`, `db.py`, `auth.py`, `categories.py`, `students.py`, `teachers.py`, `seed.py`
    - `decorators.py`, `payload.py`, `users.py`, `validation.py`
- frontend files with no tests:
    - `request.js`, `translateError.js`, `clickOutside.js`, `composables/`, `components/`, `layouts/` and `views/`
