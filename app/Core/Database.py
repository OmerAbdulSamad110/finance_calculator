from typing import AsyncIterator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import Engine
from sqlalchemy import event
from bootstrap.config import config
from contextlib import asynccontextmanager

DATABASE_URL = f"mysql+aiomysql://{config('db_username')}:{config('db_password')}@{config('db_host')}:{config('db_port')}/{config('db_database')}"

# Create Engine
engine: Engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set False in production
    pool_pre_ping=True,  # Avoid stale connections
    pool_recycle=3600,  # Auto recycle connections
)

# Session Factory
# Async Session Factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# Base Class
class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def getAysncDbContext() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Helper function for dependency injection
# 3. Define the asynchronous dependency function using 'yield'
async def getAsyncDb() -> AsyncIterator[AsyncSession]:
    async with getAysncDbContext() as session:
        yield session


# Optional: Enforce foreign keys (good practice)
# Fix: Apply event to sync_engine, not async engine
@event.listens_for(engine.sync_engine, "connect")
def setMysqlEngine(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET sql_mode='STRICT_TRANS_TABLES'")
    cursor.close()
