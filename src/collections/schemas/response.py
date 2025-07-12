from typing import Optional
import uuid
from pydantic import BaseModel, Field
from qdrant_client.models import Distance, datetime

from src.collections.constants import CollectionDbStatus
from src.embedding.constants import EmbeddingModel


class CollectionResponse(BaseModel):
    id: uuid.UUID
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
    
    class Config:
        from_attributes = True  # Allows creation from SQLAlchemy models
        populate_by_name = True

