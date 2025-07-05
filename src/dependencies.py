from typing import Annotated, AsyncGenerator

from fastapi import Depends
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3.service_resource import Bucket

from src.database import postgres_manager, redis_manager, qdrant_manager, s3_manager
from src.config import settings

async def _get_postgres() -> AsyncGenerator[AsyncSession, None]:
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

async def _get_redis() -> Redis:
    """Dependency for getting Redis client"""
    return redis_manager.get_client()

async def _get_qdrant() -> AsyncQdrantClient:
    """Dependency for getting Qdrant client"""  
    return qdrant_manager.get_client()

def bucket_dependency_factory(bucket_name: str):
    """Factory that creates a bucket dependency for a specific bucket"""
    async def get_specific_bucket() -> Bucket:
        return await s3_manager.get_bucket(bucket_name)
    return get_specific_bucket

PostgresDep = Annotated[AsyncGenerator[AsyncSession, None], Depends(_get_postgres)]
RedisDep = Annotated[Redis, Depends(_get_redis)]
QdrantDep = Annotated[AsyncQdrantClient, Depends(_get_qdrant)]
CollectionBucketDep = Annotated[Bucket, Depends(bucket_dependency_factory(settings.S3_BUCKET))]