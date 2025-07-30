from pydantic import BaseModel, Field
from qdrant_client.models import Distance

from src.collections.config import COLLECTIONSETTINGS
from src.collections.constants import CollectionDbStatus
from src.embedding.constants import EmbeddingModel


class CollectionCreate(BaseModel):
    embedding_model: EmbeddingModel
    name: str = Field(
        min_length=4,
    )
    vector_dimension: int = Field(
        gt=0,
        description="Vector dimensions must be positive",
        default=COLLECTIONSETTINGS.VECTOR_DIMENSION,
    )
    vector_distance: Distance = Field(
        description="Distance must be of enum type",
        default=COLLECTIONSETTINGS.VECTOR_DISTANCE,
    )
    vector_on_disk: bool = Field(
        description="", default=COLLECTIONSETTINGS.VECTOR_ON_DISK
    )
    shard_number: int = Field(
        default=COLLECTIONSETTINGS.SHARD_NUMBER,
        gt=0,
        description="Number of shards must be positive",
    )
    replication_factor: int = Field(
        default=COLLECTIONSETTINGS.REPLICATION_FACTOR,
        gt=0,
        description="Replication factor must be positive",
    )
    hnsw_m: int = Field(
        default=COLLECTIONSETTINGS.HNSW_M,
        ge=0,
        description="HNSW M parameter must be non-negative",
    )
    hnsw_payload_m: int = Field(
        default=COLLECTIONSETTINGS.HNSW_PAYLOAD_M,
        gt=0,
        description="HNSW payload M must be positive",
    )
    hnsw_on_disk: bool = Field(description="", default=COLLECTIONSETTINGS.HNSW_ON_DISK)
    status: CollectionDbStatus = Field(
        description="", default=COLLECTIONSETTINGS.STATUS
    )


# Usually making a new collection is better than updating an existing one
# TODO Potentially make a service to "replace" and existing collection with new parameters
class CollectionUpdate(BaseModel):
    status: CollectionDbStatus
