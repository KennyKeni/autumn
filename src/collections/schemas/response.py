import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from qdrant_client.models import Distance

from src.collections.constants import CollectionDbStatus
from src.embedding.constants import EmbeddingModel


class CollectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    embedding_model: EmbeddingModel
    vector_dimension: int
    vector_distance: Distance
    vector_on_disk: bool
    shard_number: int
    replication_factor: int
    hnsw_m: Optional[int]
    hnsw_payload_m: Optional[int]
    hnsw_on_disk: bool
    status: CollectionDbStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
    )
