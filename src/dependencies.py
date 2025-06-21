from typing import AsyncGenerator

from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from database import postgres_manager, redis_manager, qdrant_manager

async def get_postgres() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    session_maker = postgres_manager.get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_redis() -> Redis:
    """Dependency for getting Redis client"""
    return redis_manager.get_client()

async def get_qdrant() -> AsyncQdrantClient:
    """Dependency for getting Qdrant client"""  
    return qdrant_manager.get_client()