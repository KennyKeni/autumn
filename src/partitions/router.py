import uuid

from fastapi import APIRouter

from src.dependencies import PostgresDep, S3ClientDep
from src.embedding.dependencies import (EmbeddingServiceDep, EmbedModelDep,
                                        StorageContextDep,
                                        ToolStorageContextDep)
from src.files.dependencies import ValidFileDep
from src.partitions.dependencies import PartitionServiceDep, ValidPartitionDep
from src.partitions.schemas.request import CreatePartitionRequest
from src.partitions.schemas.response import PartitionResponse
from src.tools.dependencies import ToolServiceDep

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
    embedding_service: EmbeddingServiceDep,
    tool_service: ToolServiceDep,
    s3_client: S3ClientDep,
    partition_service: PartitionServiceDep,
) -> PartitionResponse:
    return await partition_service.add_partition_file(
        partition,
        file,
        tool_service,
        embedding_service,
        s3_client,
    )


@router.delete("/{partition_id}", response_model=PartitionResponse)
async def delete_partition(
    partition_id: uuid.UUID,
    session: PostgresDep,
    partition_service: PartitionServiceDep,
) -> PartitionResponse:
    return await partition_service.delete_partition(partition_id, session)
