# grade tracker

track student grades across categories and subcategories, with per-subcategory line charts

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

copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

```bash
docker compose up --build # start always rebuilding
docker compose down -v    # stop and reset volumes
```

open http://localhost

## env vars

| var            | default                 | used in                                                    |
|----------------|-------------------------|------------------------------------------------------------|
| `SECRET_KEY`   | `dev-default-value`     | flask session signing                                      |
| `ADMIN_PASS`   | `admin`                 | initial admin password (set on first run)                  |
| `FLASK_HOST`   | `127.0.0.1`             | flask bind address; set to `0.0.0.0` in docker via compose |
| `CORS_ORIGINS` | `http://localhost:5173` | allowed frontend origin                                    |

## roles

| role    | lands on              | can do                                  |
|---------|-----------------------|-----------------------------------------|
| admin   | `/admin/teachers`     | create and delete teacher accounts      |
| teacher | `/teacher/categories` | manage categories, students, and grades |
| student | `/student`            | view own grades as charts               |

default admin account: `admin` / `admin`; password can be changed from the admin screen.

## entities

- **category**: top-level grouping (e.g. serve)
- **subcategory**: belongs to a category (e.g. slice); each gets its own line chart
- **grade**: value 0.0–10.0 with one decimal, tied from a teacher to a student + subcategory + date

## test

```bash
cd backend && uv run pytest
cd frontend && npm test
```

## dev tools

seed the database with test users, categories, and a year of grades:

```bash
cd backend && uv run python seed.py
```

## codebase guides

- [BACK_READ.md](BACK_READ.md), [FRONT_READ.md](FRONT_READ.md) and [INFRA_READ.md](INFRA_READ.md): beginner-friendly
  guides for navigating the codebase
- [TODO.md](TODO.md): known improvements and future work
