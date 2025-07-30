from uuid import UUID

from qdrant_client import AsyncQdrantClient, models
from sqlalchemy.ext.asyncio import AsyncSession

from src.collections.models.collection import Collection
from src.collections.repository import CollectionSqlRepository
from src.collections.schemas.request import CreateCollectionRequest
from src.collections.schemas.response import CollectionResponse
from src.collections.utils import CollectionMapper
from src.partitions.utils import get_tool_collection


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
            **CollectionMapper.qdrant_create_collection(collection, tool_collection=False)
        )

        if success is False:
            raise Exception("PLACEHOLDER")

        success = await qdrant_client.create_collection(
            **CollectionMapper.qdrant_create_collection(collection, tool_collection=True)
        )

        if success is False:
            raise Exception("PLACEHOLDER")

        await self.create_payload_index(
            collection=collection,
            qdrant_client=qdrant_client,
            is_tenant=True,
            field_name="partition_id",
        )


        await self.create_payload_index(
            collection=collection,
            qdrant_client=qdrant_client,
            is_tenant=False,
            field_name="partition_file_id",
        )


        await self.create_payload_index(
            collection=collection,
            qdrant_client=qdrant_client,
            is_tenant=False,
            field_name="file_id",
        )


        await self.create_payload_index(
            collection=collection,
            qdrant_client=qdrant_client,
            is_tenant=True,
            field_name="partition_id",
            tool_collection=True,
        )


        await self.create_payload_index(
            collection=collection,
            qdrant_client=qdrant_client,
            is_tenant=False,
            field_name="tool_group",
            tool_collection=True,
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
        success = success and await qdrant_client.delete_collection(
            collection_name=get_tool_collection(str(collection.id)), timeout=30
        )
        if success is False:
            raise Exception("PLACEHOLDER")

        await session.commit()

        return CollectionMapper.db_to_response(collection)

    async def create_payload_index(
        self,
        collection: Collection,
        qdrant_client: AsyncQdrantClient,
        is_tenant: bool,
        field_name: str,
        tool_collection: bool = False,
    ):
        await qdrant_client.create_payload_index(
            collection_name=get_tool_collection(str(collection.id)) if tool_collection else str(collection.id),
            field_name=field_name,
            field_schema=models.KeywordIndexParams(
                type=models.KeywordIndexType.KEYWORD,
                is_tenant=is_tenant,
            ),
        )
