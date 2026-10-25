# bake mode merges stage namespaces across services; all stage names must be unique
FROM python:3.14.7-slim AS b-base
COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./

FROM b-base AS b-test
RUN uv sync --frozen
COPY . .
# lint, layout and tests must all pass, any failure stops the build
RUN uv run ruff check && uv run ruff format --check && uv run pytest && touch /app/.test-passed

FROM b-base AS b-runtime
# forces docker to build test stage first; failing checks block runtime
COPY --from=b-test /app/.test-passed /tmp/.test-passed
RUN uv sync --no-dev --frozen
# runtime needs only the app package, its entry point and the arena cli, tests stay in b-test
COPY app/ app/
COPY run.py create_arena.py ./
RUN useradd --system --no-create-home non_root_backend_user && mkdir /data && chown non_root_backend_user /data
USER non_root_backend_user
EXPOSE 5000
ENV PATH="/app/.venv/bin:$PATH"
# deliberate: runs werkzeug's dev server (app.run) in production for simplicity. lost vs a wsgi server like gunicorn:
# - one new thread per request with no cap; bursts can hit pids_limit and fail
# - no request timeout or worker recycling; a hung request is never killed
# - less hardened against slow or malformed clients; nginx in front covers only part of it
# - no access log control and no graceful reload
CMD ["python", "run.py"]
