from uuid import UUID
from fastapi import APIRouter
from httpx import request

from src.dependencies import PostgresDep
from src.partitions.dependencies import PartitionServiceDep
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

@router.delete("/{partition_id}", response_model=PartitionResponse)
async def delete_partition(
    partition_id: UUID,
    session: PostgresDep,
    partition_service: PartitionServiceDep
):
    return await partition_service.delete_partition(partition_id, session)