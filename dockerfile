# ── Stage 1: Builder ────────────────────────────────────────────
FROM python:3.14-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --locked --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]