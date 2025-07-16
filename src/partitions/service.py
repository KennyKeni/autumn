from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.embedding.service import EmbeddingService
from src.files.models.file import File
from src.partitions.models.partition import Partition
from src.partitions.models.partition_files import PartitionFile
from src.partitions.repository import PartitionSqlRepository
from src.partitions.schemas.request import CreatePartitionRequest
from src.partitions.utils import PartitionMapper


class PartitionService:
    def __init__(self, partition_repository: PartitionSqlRepository):
        self.partition_repository = partition_repository

    async def get_partition(
        self,
        partition: Partition,
    ):
        return PartitionMapper.db_to_response(partition)

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
    
    async def add_partition_file(
        self,
        partition: Partition,
        file: File,
        session: AsyncSession,
        embedding_service: EmbeddingService,
    ):
        partition_file = PartitionFile(
            partition=partition,
            file=file
        )

        await session.flush()

        # embedding_service.embed_file()

