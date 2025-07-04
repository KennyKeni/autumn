from fastapi import APIRouter

from src.dependencies import QdrantDep
from src.embedding.dependencies import EmbedModelDep, EmbeddingServiceDep
from src.embedding.models.requests import EmbedFileRequest

router = APIRouter(prefix="/embed", tags=["convo"])

@router.post("/upload", response_model=dict)
async def embed_file(
    embed_file_request: EmbedFileRequest,
    embedding_service: EmbeddingServiceDep,
    qdrant_client: QdrantDep,
    embed_model: EmbedModelDep,
):
    return await embedding_service.embed_file(qdrant_client=qdrant_client, embed_model=embed_model, embed_file_request=embed_file_request)