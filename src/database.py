from contextlib import AsyncExitStack
import contextlib
from typing import AsyncIterator, Optional
from aioboto3 import Session
from aiobotocore.config import AioConfig
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from types_aiobotocore_s3 import S3Client, S3ServiceResource
from types_aiobotocore_s3.service_resource import Bucket

from src.config import settings
from src.constants import Environment


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PostgresManager:
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None

    async def init_postgres(self):
        self._engine = create_async_engine(
            url=settings.POSTGRES_DSN.unicode_string(),
            echo=(settings.ENVIRONMENT != Environment.PRODUCTION),
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "server_settings": {
                    "application_name": "fastapi_rag_app",
                    "timezone": "UTC",
                },
            },
        )

        self._session_maker = async_sessionmaker(
            autocommit=False,
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close_postgres(self):
        """Shutdowns Postgres and resets variables"""
        if self._engine:
            await self._engine.dispose()

        self._engine = None
        self._session_maker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized")

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # def get_session_maker(self) -> async_sessionmaker[AsyncSession]:
    #     """Get the session maker with proper type checking"""
    #     if self._session_maker is None:
    #         raise RuntimeError("Database not initialized. Call init_db() first.")
    #     return self._session_maker


class RedisManager:
    def __init__(self):
        self._client: Optional[Redis] = None

    async def init_redis(self):
        self._client = from_url(
            settings.REDIS_DSN.unicode_string(),
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
        )

        # Connection Test
        await self._client.ping()

    async def close_redis(self):
        if self._client:
            await self._client.aclose()

    def get_client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis not initialized. Call init_redis() first.")
        return self._client


class QdrantManager:
    def __init__(self):
        self._client: Optional[AsyncQdrantClient] = None

    async def init_qdrant(self):
        self._client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_HTTP_PORT,
            api_key=settings.QDRANT_API_KEY,
            timeout=settings.QDRANT_TIMEOUT,
            https=False,
        )

        # Connection Test
        await self._client.get_collections()

    async def close_qdrant(self):
        if self._client:
            await self._client.close()

    def get_client(self) -> AsyncQdrantClient:
        if self._client is None:
            raise RuntimeError("Qdrant not initialized. Call init_qdrant() first.")
        return self._client


class S3Manager:
    def __init__(
        self,
        region: str = "auto",
        max_pool_connections: int = 50,
        connect_timeout: int = 10,
        read_timeout: int = 60,
    ):
        self._context_stack: Optional[AsyncExitStack]
        self.region = region
        self.session: Session = Session(
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=self.region,
        )
        self._client: Optional[S3Client]
        self._resource: Optional[S3ServiceResource]

        self.config = AioConfig(
            max_pool_connections=max_pool_connections,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            retries={"max_attempts": 6, "mode": "standard"},
            tcp_keepalive=True,
            request_checksum_calculation="WHEN_REQUIRED",
            response_checksum_validation="WHEN_REQUIRED",
        )

    async def init_s3(self):
        """Initialize S3 (R2) connection"""
        self._context_stack = AsyncExitStack()

        self._client = await self._context_stack.enter_async_context(
            self.session.client(
                service_name="s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                config=self.config,
            )
        )

        self._resource = await self._context_stack.enter_async_context(
            self.session.resource(
                "s3",
                region_name=self.region,
                endpoint_url=settings.S3_ENDPOINT_URL,
                config=self.config,
            )
        )

    async def close_s3(self):
        if self._context_stack:
            await self._context_stack.aclose()

        self._client = None
        self._resource = None

    def get_client(self) -> S3Client:
        if not self._client:
            raise RuntimeError("S3 not intialized. Call init_s3() first.")
        return self._client

    def get_resource(self) -> S3ServiceResource:
        if not self._resource:
            raise RuntimeError("S3 not intialized. Call init_s3() first.")
        return self._resource

    async def get_bucket(self, bucket_name: str) -> Bucket:
        resource = self.get_resource()
        return await resource.Bucket(bucket_name)


postgres_manager = PostgresManager()
redis_manager = RedisManager()
qdrant_manager = QdrantManager()
s3_manager = S3Manager()
