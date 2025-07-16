from uuid import UUID
from qdrant_client import AsyncQdrantClient, models
from sqlalchemy.ext.asyncio import AsyncSession

from src.collections.models.collection import Collection
from src.collections.repository import CollectionSqlRepository
from src.collections.schemas.request import CreateCollectionRequest
from src.collections.schemas.response import CollectionResponse
from src.collections.utils import CollectionMapper


class CollectionService:
    def __init__(self, collection_repository: CollectionSqlRepository):
        self.collection_repository: CollectionSqlRepository = collection_repository

    async def create_collection(
        self,
        request: CreateCollectionRequest,
        qdrant_client: AsyncQdrantClient,
        session: AsyncSession,
    ) -> CollectionResponse:
        collection = await self.collection_repository.create(
            CollectionMapper.to_collection_create(request)
        )
        await session.flush()
        success = await qdrant_client.create_collection(
            **CollectionMapper.qdrant_create_collection(collection)
        )

        if success is False:
            raise Exception("PLACEHOLDER")
        
        await self.create_tenant_payload_index(
            collection,
            qdrant_client
        )
    
        return CollectionMapper.db_to_response(collection)

    async def delete_collection(
        self,
        collection_id: UUID,
        qdrant_client: AsyncQdrantClient,
        session: AsyncSession,
    ) -> CollectionResponse:
        collection = await self.collection_repository.delete_by_id(collection_id, True)
        if collection is None:
            raise Exception("PLACEHOLDER")

        success = await qdrant_client.delete_collection(
            collection_name=str(collection.id), timeout=30
        )
        if success is False:
            raise Exception("PLACEHOLDER")

        await session.commit()

        return CollectionMapper.db_to_response(collection)
    
    async def create_tenant_payload_index(
        self,
        collection: Collection,
        qdrant_client: AsyncQdrantClient,
        field_name: str = "partition_id"
    ):
        await qdrant_client.create_payload_index(
            collection_name=str(collection.id),
            field_name=field_name,
            field_schema=models.KeywordIndexParams(
                type=models.KeywordIndexType.KEYWORD,
                is_tenant=True,
            ),
        )
