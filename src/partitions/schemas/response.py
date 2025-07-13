from typing import Optional
import uuid

from pydantic import BaseModel, ConfigDict

from src.partitions.constants import PartitionDbStatus


class PartitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    collection_id: uuid.UUID
    status: PartitionDbStatus

    model_config = ConfigDict(
        from_attributes = True,
    )