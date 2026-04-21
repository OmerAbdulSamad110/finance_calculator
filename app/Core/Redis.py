# app/Core/Redis.py
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import redis as syncredis
from bootstrap.config import config


def __setUrl(db: int | None = None) -> str:
    if db is None:
        db = config("redis_db")
    username = config("redis_username")
    password = config("redis_password")
    host = config("redis_host")
    port = config("redis_port")

    if password:
        return f"redis://{username}:{password}@{host}:{port}/{db}"
    return f"redis://{username}@{host}:{port}/{db}"


# Module-level singletons
_async_client: aioredis.Redis | None = None
_sync_client: syncredis.Redis | None = None


def __initRedis(db: int | None = None):
    global _async_client, _sync_client
    _async_client = aioredis.from_url(__setUrl(db), decode_responses=True)
    _sync_client = syncredis.from_url(__setUrl(db), decode_responses=True)


async def __closeRedis():
    global _async_client, _sync_client
    if _async_client:
        await _async_client.aclose()
    if _sync_client:
        _sync_client.close()


@asynccontextmanager
async def setupRedis():
    __initRedis()
    try:
        yield
    finally:
        await __closeRedis()


def getAsyncRedis() -> aioredis.Redis:
    if not _async_client:
        raise RuntimeError("Redis not initialized — call initRedis() first")
    return _async_client


def getSyncRedis() -> syncredis.Redis:
    if not _sync_client:
        raise RuntimeError("Redis not initialized — call initRedis() first")
    return _sync_client
