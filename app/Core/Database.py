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


# Helper function for dependency injection
# 3. Define the asynchronous dependency function using 'yield'
async def get_async_db() -> AsyncIterator[AsyncSession]:
    """
    Provides an encapsulated, asynchronous database session.
    The code before 'yield' runs before the request.
    The code after 'yield' runs after the response is sent.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Optional: Enforce foreign keys (good practice)
# Fix: Apply event to sync_engine, not async engine
@event.listens_for(engine.sync_engine, "connect")
def set_mysql_engine(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET sql_mode='STRICT_TRANS_TABLES'")
    cursor.close()
