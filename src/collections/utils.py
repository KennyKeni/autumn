from typing import Any, Dict

from qdrant_client.models import HnswConfigDiff, SparseVectorParams, VectorParams

from src.collections.models.collection import Collection
from src.collections.models.repository import CollectionCreate
from src.collections.schemas.request import CreateCollectionRequest
from src.collections.schemas.response import CollectionResponse
from src.partitions.utils import get_tool_collection


class CollectionMapper:
    @staticmethod
    def qdrant_create_collection(
        collection: Collection, tool_collection: bool = False
    ) -> Dict[str, Any]:
        """Convert CollectionCreate to Qdrant create_collection parameters"""
        return {
            "collection_name": (
                get_tool_collection(collection.id)
                if tool_collection
                else str(collection.id)
            ),
            "vectors_config": {
                "text-dense": VectorParams(
                    size=collection.vector_dimension,
                    distance=collection.vector_distance,
                    on_disk=collection.vector_on_disk,
                )
            },
            "hnsw_config": HnswConfigDiff(
                m=collection.hnsw_m,
                payload_m=collection.hnsw_payload_m,
                on_disk=collection.hnsw_on_disk,
            ),
            "replication_factor": collection.replication_factor,
            "shard_number": collection.shard_number,
            "sparse_vectors_config": {"text-sparse-new": SparseVectorParams()},
        }

    @staticmethod
    def db_to_response(collection: Collection) -> CollectionResponse:
        """Convert Collection SQLAlchemy model to response model"""
        return CollectionResponse.model_validate(collection)

    @staticmethod
    def to_collection_create(request: CreateCollectionRequest) -> CollectionCreate:
        return CollectionCreate(**request.model_dump(exclude_unset=True))
