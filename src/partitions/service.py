from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.partitions.repository import PartitionSqlRepository
from src.partitions.schemas.request import CreatePartitionRequest
from src.partitions.utils import PartitionMapper


class PartitionService:
    def __init__(self, partition_repository: PartitionSqlRepository):
        self.partition_repository = partition_repository

    async def create_partition(
        self, 
        request: CreatePartitionRequest,
        session: AsyncSession,
    ):
        partition = await self.partition_repository.create(PartitionMapper.to_partition_create(request))
        await session.commit()

        return PartitionMapper.db_to_response(partition)
    
    async def delete_partition(
        self, 
        partition_id: UUID,
        session: AsyncSession,
    ):
        partition = await self.partition_repository.delete_by_id(partition_id)
        if not partition:
            return Exception("Placeholder")
        
        await session.commit()
        return PartitionMapper.db_to_response(partition)