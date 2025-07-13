from typing import Optional

from pydantic import BaseModel, Field
from qdrant_client.models import Distance

from src.embedding.constants import EmbeddingModel


class CreateCollectionRequest(BaseModel):
    embedding_model: EmbeddingModel
    vector_dimension: Optional[int] = Field(
        default=None, gt=0, description="Vector dimensions must be positive"
    )
    vector_distance: Optional[Distance] = Field(
        default=None, description="Distance must be of enum type"
    )
