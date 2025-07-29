from uuid import UUID

from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from src.embedding.service import EmbeddingService
from src.exceptions import DuplicateEntityError
from src.files.models.file import File
from src.partitions.models.partition import Partition
from src.partitions.models.partition_file import PartitionFile
from src.partitions.models.repository import PartitionFileCreate
from src.partitions.repository import (PartitionFileSqlRepository,
                                       PartitionSqlRepository)
from src.partitions.schemas.request import CreatePartitionRequest
from src.partitions.schemas.response import PartitionResponse
from src.partitions.utils import PartitionMapper


class PartitionService:
    def __init__(
        self, 
        partition_repository: PartitionSqlRepository, 
        partition_file_repository: PartitionFileSqlRepository,
    ) -> None:
        self.partition_repository = partition_repository
        self.partition_file_repository = partition_file_repository

    async def get_partition(
        self,
        partition: Partition,
    ) -> PartitionResponse:
        return PartitionMapper.db_to_response(partition)
    
    async def create_partition(
        self, 
        request: CreatePartitionRequest,
        session: AsyncSession,
    ) -> PartitionResponse:
        partition = await self.partition_repository.create(PartitionMapper.to_partition_create(request))
        await session.flush()

        return PartitionMapper.db_to_response(partition)
    
    async def delete_partition(
        self, 
        partition_id: UUID,
        session: AsyncSession,
    ) -> PartitionResponse:
        partition = await self.partition_repository.delete_by_id(partition_id)
        if not partition:
            raise Exception("Placeholder")
        
        await session.commit()
        return PartitionMapper.db_to_response(partition)
    
    async def add_partition_file(
        self,
        partition: Partition,
        file: File,
        embed_mode: OpenAILikeEmbedding,
        embedding_service: EmbeddingService,
        s3_client: S3Client,
    ) -> bool:
        # TODO: Bake this into repository create
        partition_file_exist = await self.partition_file_repository.get_partition_file_from_fk(
            partition.id,
            file.id,
        )
        if partition_file_exist:
            raise DuplicateEntityError(PartitionFile)

        partition_file = await self.partition_file_repository.create(
            PartitionFileCreate(
                partition=partition,
                partition_id=partition.id,
                file=file,
                file_id=file.id,
            )
        )

        await embedding_service.embed_file(
            partition_file,
            embed_mode, 
            s3_client,
        )

        return True

