from qdrant_client.models import HnswConfigDiff, VectorParams

from src.collections.models.collection import Collection
from src.collections.models.repository import CollectionCreate
from src.collections.schemas.request import CreateCollectionRequest
from src.collections.schemas.response import CollectionResponse


class CollectionMapper:
    @staticmethod
    def qdrant_create_collection(collection: Collection) -> dict:
        """Convert CollectionCreate to Qdrant create_collection parameters"""
        return {
            "collection_name": str(collection.id),
            "vectors_config": VectorParams(
                size=collection.vector_dimension,
                distance=collection.vector_distance,
                on_disk=collection.vector_on_disk,
            ),
            "hnsw_config": HnswConfigDiff(
                m=collection.hnsw_m,
                payload_m=collection.hnsw_payload_m,
                on_disk=collection.hnsw_on_disk,
            ),
            "replication_factor": collection.replication_factor,
            "shard_number": collection.shard_number,
        }

    @staticmethod
    def db_to_response(collection: Collection) -> CollectionResponse:
        """Convert Collection SQLAlchemy model to response model"""
        return CollectionResponse.model_validate(collection)
    
    @staticmethod
    def to_collection_create(request: CreateCollectionRequest) -> CollectionCreate:
        return CollectionCreate(**request.model_dump(exclude_unset=True))