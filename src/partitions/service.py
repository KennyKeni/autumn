from uuid import UUID
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from qdrant_client import AsyncQdrantClient, QdrantClient
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client
from src.embedding.service import EmbeddingService
from src.exceptions import DuplicateEntityError
from src.files.models.file import File
from src.partitions.models.partition import Partition
from src.partitions.models.partition_files import PartitionFile
from src.partitions.repository import PartitionSqlRepository
from src.partitions.schemas.request import CreatePartitionRequest
from src.partitions.utils import PartitionMapper, partition_file_exist_stmt


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
        await session.flush()

        return PartitionMapper.db_to_response(partition)
    
    async def delete_partition(
        self, 
        partition_id: UUID,
        session: AsyncSession,
    ):
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
        session: AsyncSession,
        embedding_service: EmbeddingService,
        qdrant_client: AsyncQdrantClient,
        qdrant_sync_client: QdrantClient,
        s3_client: S3Client,
    ):
        partition_file_exist = await session.scalar(partition_file_exist_stmt(partition.id, file.id))
        if partition_file_exist is not None:
            raise DuplicateEntityError(PartitionFile)

        partition_file = PartitionFile(
            partition=partition,
            file=file
        )
        session.add(partition_file)
        await session.commit()

        await embedding_service.embed_file(partition_file, embed_mode, qdrant_client, qdrant_sync_client, s3_client)

        return True

