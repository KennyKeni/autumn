from contextlib import AsyncExitStack
from typing import Optional
from aioboto3 import Session
from aiobotocore.config import AioConfig
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from types_aiobotocore_s3 import S3Client, S3ServiceResource
from types_aiobotocore_s3.service_resource import Bucket

from src.config import settings
from src.constants import Environment


class Base(AsyncAttrs, DeclarativeBase):
    pass

class PostgresManager:
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.async_session: Optional[async_sessionmaker[AsyncSession]] = None

    async def init_postgres(self):
        self.engine = create_async_engine(
            url=settings.POSTGRES_DSN.unicode_string(),
            echo=(settings.ENVIRONMENT != Environment.PRODUCTION),

            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,

            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,

            # connect_args={
            #     "statement_cache_size": 0,  
            #     "prepared_statement_cache_size": 0,
            # }
        )

        self.async_session = async_sessionmaker(
            url=settings.POSTGRES_DSN.unicode_string(),
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close_postgres(self):
        if self.engine:
            await self.engine.dispose()
    
    def get_session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Get the session maker with proper type checking"""
        if self.async_session is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.async_session


class RedisManager:
    def __init__(self):
        self.client: Optional[Redis] = None

    async def init_redis(self):
        self.client = from_url(
            settings.REDIS_DSN.unicode_string(),
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
        )

        # Connection Test
        await self.client.ping()
    
    async def close_redis(self):
        if self.client:            
            await self.client.aclose()

    def get_client(self) -> Redis:
        if self.client is None:
            raise RuntimeError("Redis not initialized. Call init_redis() first.")
        return self.client


class QdrantManager:
    def __init__(self):
        self.client: Optional[AsyncQdrantClient] = None

    async def init_qdrant(self):
        self.client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_HTTP_PORT,
            api_key=settings.QDRANT_API_KEY,
            timeout=settings.QDRANT_TIMEOUT,
            https=False,
        )

        # Connection Test
        await self.client.get_collections()

    async def close_qdrant(self):
        if self.client:
            await self.client.close()

    def get_client(self) -> AsyncQdrantClient:
        if self.client is None:
            raise RuntimeError("Qdrant not initialized. Call init_qdrant() first.")
        return self.client

class S3Manager:
    def __init__(
        self, 
        region: str = "auto",
        max_pool_connections: int = 50,
        connect_timeout: int = 10,
        read_timeout: int = 60
    ):
        self.context_stack: AsyncExitStack
        self.region = region
        self.session: Session = Session()
        self.client: Optional[S3Client]
        self.resource: Optional[S3ServiceResource]

        self.config = AioConfig(
            max_pool_connections=max_pool_connections,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            retries={'max_attempts': 6, 'mode': 'standard'},
            tcp_keepalive=True
        )

    async def init_s3(self):
        """Initialize S3 (R2) connection"""
        self.context_stack = AsyncExitStack()
        
        self.client = await self.context_stack.enter_async_context(
            self.session.client(
                service_name="s3",
                region_name=self.region, 
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                config=self.config,
            )
        )

        self.resource = await self.context_stack.enter_async_context(
            self.session.resource(
                's3',
                region_name=self.region,
                endpoint_url=settings.S3_ENDPOINT_URL,
            )
        )

    async def close_s3(self):
        if self.context_stack:
            await self.context_stack.aclose()
        
        self.client = None
        self.resource = None

    def get_client(self) -> S3Client:
        if not self.client:
            raise RuntimeError("S3 not intialized. Call init_s3() first.")
        return self.client
    
    def get_resource(self) -> S3ServiceResource:
        if not self.resource:
            raise RuntimeError("S3 not intialized. Call init_s3() first.")
        return self.resource
    
    async def get_bucket(self, bucket_name: str) -> Bucket:
        resource = self.get_resource()
        return await resource.Bucket(bucket_name)

postgres_manager = PostgresManager()
redis_manager = RedisManager()
qdrant_manager = QdrantManager()
s3_manager = S3Manager()