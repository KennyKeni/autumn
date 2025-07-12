from typing import Optional
from pydantic import BaseModel
from qdrant_client.grpc import CreateCollection
from qdrant_client.models import Distance

from src.collections.constants import CollectionDbStatus
from src.embedding.constants import EmbeddingModel
from src.collections.config import collectionSettings


from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    embedding_model: EmbeddingModel
    vector_dimension: int = Field(
        gt=0,
        description="Vector dimensions must be positive",
        default=collectionSettings.VECTOR_DIMENSION,
    )
    vector_distance: Distance = Field(
        description="Distance must be of enum type",
        default=collectionSettings.VECTOR_DISTANCE,
    )
    vector_on_disk: bool = Field(
        description="", default=collectionSettings.VECTOR_ON_DISK
    )
    shard_number: int = Field(
        default=collectionSettings.SHARD_NUMBER,
        gt=0,
        description="Number of shards must be positive",
    )
    replication_factor: int = Field(
        default=collectionSettings.REPLICATION_FACTOR,
        gt=0,
        description="Replication factor must be positive",
    )
    hnsw_m: int = Field(
        default=collectionSettings.HNSW_M,
        ge=0,
        description="HNSW M parameter must be non-negative",
    )
    hnsw_payload_m: int = Field(
        default=collectionSettings.HNSW_PAYLOAD_M,
        gt=0,
        description="HNSW payload M must be positive",
    )
    hnsw_on_disk: bool = Field(description="", default=collectionSettings.HNSW_ON_DISK)
    status: CollectionDbStatus = Field(
        description="", default=collectionSettings.STATUS
    )


# Usually making a new collection is better than updating an existing one
# TODO Potentially make a service to "replace" and existing collection with new parameters
class CollectionUpdate(BaseModel):
    status: CollectionDbStatus = collectionSettings.STATUS
