FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./

FROM base AS test
RUN uv sync --frozen
COPY . .
RUN uv run pytest && touch /app/.test-passed

FROM base AS runtime
COPY --from=test /app/.test-passed /tmp/.test-passed  # forces docker to build test stage first; failing tests block runtime
RUN uv sync --no-dev --frozen
COPY . .
EXPOSE 5000
CMD ["uv", "run", "python", "run.py"]
