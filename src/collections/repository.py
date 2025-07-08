from qdrant_client import QdrantClient
from src.repository import QdrantRepository, SqlRepository
from sqlalchemy.ext.asyncio import AsyncSession


class CollectionSqlRepository(SqlRepository):
    def __init__(self, postgres_session: AsyncSession):
        super().__init__(postgres_session)


class CollectionQdrantRepository(QdrantRepository):
    def __init__(self, qdrant_client: QdrantClient):
        super().__init__(qdrant_client)
