from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.collections.constants import CollectionDbStatus
from src.collections.models.collection import Collection
from src.collections.models.repository import (CollectionCreate,
                                               CollectionUpdate)
from src.repository import QdrantRepository, SqlRepository


class CollectionSqlRepository(
    SqlRepository[Collection, CollectionCreate, CollectionUpdate]
):
    def __init__(self, postgres_session: AsyncSession):
        super().__init__(
            postgres_session,
            Collection,
            Collection.status != CollectionDbStatus.DELETED,
        )


class CollectionQdrantRepository(QdrantRepository):
    def __init__(self, qdrant_client: QdrantClient):
        super().__init__(qdrant_client)
