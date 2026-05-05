# ── Stage 1: Builder ────────────────────────────────────────────
FROM python:3.14-slim-bookworm

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN mkdir -p logs && touch logs/app.log

RUN uv sync --locked --no-dev
RUN uv add --dev debugpy black

COPY . .

EXPOSE 8000 5678
CMD ["uv", "run", "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]