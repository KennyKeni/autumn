from uuid import UUID
from fastapi import APIRouter
from httpx import request

from src.dependencies import PostgresDep, QdrantDep, QdrantSyncDep, S3ClientDep
from src.embedding.dependencies import EmbedModelDep, EmbeddingServiceDep
from src.files.dependencies import ValidFileDep
from src.partitions.dependencies import PartitionServiceDep, ValidPartitionDep
from src.partitions.schemas.request import CreatePartitionRequest
from src.partitions.schemas.response import PartitionResponse


router = APIRouter(prefix="/partitions", tags=["partitions"])

@router.post("", response_model=PartitionResponse)
async def create_partition(
    request: CreatePartitionRequest,
    session: PostgresDep,
    partition_service: PartitionServiceDep,
) -> PartitionResponse:
    return await partition_service.create_partition(request, session)

@router.post("/{partition_id}/files/{file_id}")
async def add_partition_file(
    partition: ValidPartitionDep,
    file: ValidFileDep,
    embed_model: EmbedModelDep,
    session: PostgresDep,
    embedding_service: EmbeddingServiceDep,
    partition_service: PartitionServiceDep,
    qdrant_client: QdrantDep,
    qdrant_sync_client: QdrantSyncDep,
    s3_client: S3ClientDep,
):
    return await partition_service.add_partition_file(
        partition, 
        file, 
        embed_model, 
        session, 
        embedding_service, 
        qdrant_client,
        qdrant_sync_client,
        s3_client,
    )


@router.delete("/{partition_id}", response_model=PartitionResponse)
async def delete_partition(
    partition_id: UUID,
    session: PostgresDep,
    partition_service: PartitionServiceDep
):
    return await partition_service.delete_partition(partition_id, session)