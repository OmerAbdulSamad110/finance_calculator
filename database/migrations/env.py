import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from bootstrap.config import config as env

# ── Alembic Config ──────────────────────────────────────────────
alembic_config = context.config
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# ── Your Base metadata ──────────────────────────────────────────
from app.Models.Model import Base  # adjust to your project path

target_metadata = Base.metadata

# ── Build async DATABASE_URL ────────────────────────────────────
DATABASE_URL = f"mysql+aiomysql://{env('db_username')}:{env('db_password')}@{env('db_host')}:{env('db_port')}/{env('db_database')}"


# ── Offline mode ────────────────────────────────────────────────
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (async) ─────────────────────────────────────────
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(
        DATABASE_URL,
        echo=env("debug"),
        pool_pre_ping=env("debug"),
        pool_recycle=3600,
        poolclass=pool.NullPool,  # ← critical for Alembic
    )

    async with engine.begin() as conn:
        await conn.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ─────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
