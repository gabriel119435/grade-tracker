# bake mode merges stage namespaces across services; all stage names must be unique
FROM python:3.12-slim AS b-base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./

FROM b-base AS b-test
RUN uv sync --frozen
COPY . .
RUN uv run pytest && touch /app/.test-passed

FROM b-base AS b-runtime
# forces docker to build test stage first; failing tests block runtime
COPY --from=b-test /app/.test-passed /tmp/.test-passed
RUN uv sync --no-dev --frozen
COPY . .
EXPOSE 5000
CMD ["uv", "run", "python", "run.py"]
