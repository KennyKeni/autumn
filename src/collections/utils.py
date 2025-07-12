from qdrant_client.models import HnswConfigDiff, VectorParams
from src.collections.models.collection import Collection
from src.collections.models.repository import CollectionCreate
from src.collections.schemas.response import CollectionResponse


class CollectionMapper:
    """Maps between SQL Model and Qdrant API"""

    @classmethod
    def qdrant_create_collection(cls, collection: Collection) -> dict:
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
        # return CreateCollectionResponse(
        #     id=collection.id,
        #     embedding_model=collection.embedding_model,
        #     vector_dimension=collection.vector_dimension,
        #     vector_distance=collection.vector_distance,
        #     vector_on_disk=collection.vector_on_disk,
        #     shard_number=collection.shard_number,
        #     replication_factor=collection.replication_factor,
        #     hnsw_m=collection.hnsw_m,
        #     hnsw_payload_m=collection.hnsw_payload_m,
        #     hnsw_on_disk=collection.hnsw_on_disk,
        #     status=collection.status,
        #     created_at=collection.created_at,
        #     updated_at=collection.updated_at,
        # )