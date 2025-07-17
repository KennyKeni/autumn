
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client.models import Distance

from src.collections.constants import CollectionDbStatus
from src.embedding.constants import EmbeddingModel

# Default values to be used in Models


class CollectionConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="COLLECTIONS_",
        extra="ignore",
    )

    EMBEDDING_MODEL: EmbeddingModel = Field(
        default=EmbeddingModel.QWEN3_8B, description="Embedding model of the collection"
    )
    VECTOR_DIMENSION: int = Field(
        default=4096, description="Vector dimensions of the embedding"
    )
    VECTOR_DISTANCE: Distance = Field(
        default=Distance.COSINE,
        description="Distance formula used for similarity calculations",
    )
    VECTOR_ON_DISK: bool = Field(
        default=False, description="Whether to store vectors on disk"
    )
    SHARD_NUMBER: int = Field(
        default=1, description="Number of shards for the collection"
    )
    REPLICATION_FACTOR: int = Field(
        default=1, description="Replication factor for the collection"
    )
    HNSW_M: int = Field(
        default=0,
        description="HNSW M parameter for indexing, optimized for multi-tenant",
    )
    HNSW_PAYLOAD_M: int = Field(
        default=16, description="HNSW payload M parameter, optimized for multi-tenant"
    )
    HNSW_ON_DISK: bool = Field(
        default=False, description="Whether to store HNSW index on disk"
    )
    STATUS: CollectionDbStatus = Field(
        default=CollectionDbStatus.ACTIVE, description="Collection status"
    )


collectionSettings = CollectionConfig()  # type: ignore
