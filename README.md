# grade tracker

track student grades across categories and subcategories, with per-subcategory line charts

![teacher grades view](teacher-grades-view.png)

## stack

- **backend**: python, flask, sqlalchemy, sqlite; pytest for tests
- **frontend**: vue 3 (script setup), vite, vue-router, vue-i18n, chart.js; vitest for tests
- **infra**: docker, nginx (reverse proxy, rate limiting, static file serving)

## run (local)

```bash
cd backend && uv sync
cd frontend && npm install
```

```bash
cd backend && uv run python run.py   # http://localhost:5000
cd frontend && npm run dev           # http://localhost:5173
```

open http://localhost:5173

## run (docker)

```bash
docker compose up --build # always rebuilds it
docker compose down -v    # stops and deletes volumes
```

open http://localhost

## config

if no `.env` is configured, the app uses insecure public defaults values.
to set your own values, copy `.env.example` to `.env` and edit it:

```bash
cp .env.example .env
```

`DEFAULT_ARENA_NAME`, `DEFAULT_ADMIN_NAME` and `DEFAULT_ADMIN_PASS` are only used when db is built.
an unset or empty var falls back to its default below.

## env vars

| var                     | default             | used in                                                    |
|-------------------------|---------------------|------------------------------------------------------------|
| `SECRET_KEY`            | `dev-default-value` | flask session signing                                      |
| `SESSION_COOKIE_SECURE` | `0`                 | `1` sends the session cookie only over https               |
| `DEFAULT_ARENA_NAME`    | `arena de teste`    | initial arena name (set on first run)                      |
| `DEFAULT_ADMIN_NAME`    | `administrador`     | initial admin username (set on first run)                  |
| `DEFAULT_ADMIN_PASS`    | `senha primaria`    | initial admin password (set on first run)                  |
| `DEFAULT_SEED_PASS`     | `senha secundaria`  | password of every seeded user                              |
| `FLASK_HOST`            | `127.0.0.1`         | flask bind address; set to `0.0.0.0` in docker via compose |
| `FLASK_DEBUG`           | `1`                 | reloader and debugger; set to `0` in docker via compose    |
| `DATABASE_URL`          | `backend/app.db`    | sqlalchemy db url; docker points it to the `/data` volume  |

## arenas

each arena is fully isolated: its users, categories and grades are invisible to every other arena.
each arena has exactly one admin.

```bash
cd backend && uv run create_arena.py <arena> <admin> <password>                     # local
docker compose exec flask-backend python create_arena.py <arena> <admin> <password> # docker
```

## roles

| role    | lands on              | can do                                                        |
|---------|-----------------------|---------------------------------------------------------------|
| admin   | `/admin`              | create and delete teacher accounts, change own password, seed |
| teacher | `/teacher/categories` | manage categories, students, and grades                       |
| student | `/student`            | view own grades as charts                                     |

default admin account: `DEFAULT_ADMIN_NAME` / `DEFAULT_ADMIN_PASS` in arena `DEFAULT_ARENA_NAME`.

seed button: wipes the admin's arena except the admin, then creates demo data; seeded users use `DEFAULT_SEED_PASS`.

## entities

- **arena**: outermost entity, every user and category belongs to one arena
- **category**: top-level grouping (e.g. serve)
- **subcategory**: belongs to a category (e.g. strength); each gets its own line chart
- **grade**: value 0.0–10.0 with one decimal, tied from a teacher to a student + subcategory + date

## test

```bash
cd backend && uv run pytest
cd frontend && npm test
```

## codebase guides

- [FRONT_BASICS.md](FRONT_BASICS.md): frontend concepts from scratch
- [BACK_READ.md](BACK_READ.md), [FRONT_READ.md](FRONT_READ.md) and [INFRA_READ.md](INFRA_READ.md): beginner guides
- [TODO.md](TODO.md): known improvements and future work
