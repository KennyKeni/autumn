import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.chat.router import router as chat_router
from src.collections.router import router as collections_router
from src.config import SETTINGS
from src.constants import Environment
from src.embedding.router import router as embedding_router
from src.files.router import router as files_router
from src.lifespan import lifespan
from src.partitions.router import router as partitions_router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Autumn", version=SETTINGS.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=SETTINGS.CORS_HEADERS,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    from src.lifespan import check_services_health

    services_status = await check_services_health()
    all_healthy = all(services_status.values())

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "services": services_status,
    }


app.include_router(embedding_router)
app.include_router(files_router)
app.include_router(collections_router)
app.include_router(partitions_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=SETTINGS.ENVIRONMENT != Environment.PRODUCTION,
    )
