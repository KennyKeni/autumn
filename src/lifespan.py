import asyncio
import logging

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from win32com.server import exception

from src.database import postgres_manager, redis_manager, qdrant_manager, s3_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    startup_tasks = []

    try:
        # Initialize all services concurrently
        startup_tasks = await asyncio.gather(
            _init_postgres(),
            _init_redis(),
            _init_qdrant(),
            _init_s3(),
            return_exceptions=False,
        )

        for i, result in enumerate(startup_tasks):
            if isinstance(result, Exception):
                service_names = ["Database", "Redis", "Qdrant"]
                logger.error(f"Failed to initialize {service_names[i]}: {result}")
                raise result

        logger.info("All services initialized successfully")

        app.state.services_ready = True

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        await _cleanup_on_startup_failure()
        raise

    # ========== APPLICATION RUNNING ==========
    yield

    # ========== SHUTDOWN ==========
    logger.info("Application shutdown initiated...")

    try:
        await asyncio.gather(
            _shutdown_database(),
            _shutdown_redis(),
            _shutdown_qdrant(),
            _shutdown_s3(),
            return_exceptions=True,
        )

    except Exception as e:
        logger.error(f"Shutdown warning: {e}")

    logger.info("Application shutdown complete")


async def _cleanup_on_startup_failure() -> None:
    """Clean up any partially initialized services on startup failure"""
    logger.info("Cleaning up partially initialized services...")

    cleanup_tasks = [
        _shutdown_database(),
        _shutdown_redis(),
        _shutdown_qdrant(),
    ]

    await asyncio.gather(*cleanup_tasks, return_exceptions=True)
    logger.info("Cleanup complete")


async def check_services_health() -> dict[str, bool]:
    """Check the health of all services"""
    health_status = {}

    try:
        postgres_manager.connect()
        health_status["postgres"] = True
    except Exception:
        health_status["postgres"] = False

    try:
        redis_client = redis_manager.get_client()
        await redis_client.ping()
        health_status["redis"] = True
    except Exception:
        health_status["redis"] = False

    try:
        qdrant_client = qdrant_manager.get_client()
        await qdrant_client.get_collections()
        health_status["qdrant"] = True
    except Exception:
        health_status["qdrant"] = False

    return health_status


# Helper Functions for Databases
async def _init_postgres() -> None:
    """Initialize database connection with error handling"""
    try:
        await postgres_manager.init_postgres()
        logging.info("Postgres Connected")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def _init_redis() -> None:
    """Initialize Redis connection with error handling"""
    try:
        await redis_manager.init_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Redis initialization failed: {e}")
        raise


async def _init_qdrant() -> None:
    """Initialize Qdrant connection with error handling"""
    try:
        await qdrant_manager.init_qdrant()
        logger.info("Qdrant connected")
    except Exception as e:
        logger.error(f"Qdrant initialization failed: {e}")
        raise


async def _init_s3() -> None:
    """Initialize S3 connection with error handling"""
    try:
        await s3_manager.init_s3()
        logger.info("S3 connected")
    except Exception as e:
        logger.error(f"S3 initialization failed: {e}")
        raise


async def _shutdown_database() -> None:
    """Shutdown database with error handling"""
    try:
        await postgres_manager.close_postgres()
        logger.info("Database disconnected")
    except Exception as e:
        logger.warning(f"Database shutdown warning: {e}")


async def _shutdown_redis() -> None:
    """Shutdown Redis with error handling"""
    try:
        await redis_manager.close_redis()
        logger.info("Redis disconnected")
    except Exception as e:
        logger.warning(f"Redis shutdown warning: {e}")


async def _shutdown_qdrant() -> None:
    """Shutdown Qdrant with error handling"""
    try:
        await qdrant_manager.close_qdrant()
        logger.info("Qdrant disconnected")
    except Exception as e:
        logger.warning(f"Qdrant shutdown warning: {e}")


async def _shutdown_s3() -> None:
    """Shutdown S3 with error handling"""
    try:
        await s3_manager.close_s3()
        logger.info("S3 disconnected")
    except Exception as e:
        logger.warning(f"S3 shutdown warning: {e}")
