import uuid
from typing import Optional

from pydantic import BaseModel, Field

from src.partitions.constants import PartitionDbStatus


class CreatePartitionRequest(BaseModel):
    name: str = Field(..., min_length=4, description="Partition name")
    description: Optional[str] = Field(None, min_length=4, description="Partition description")
    collection_id: uuid.UUID

class UpdatePartitionRequest(BaseModel):
    name: str = Field(..., min_length=4, description="Partition name")
    description: Optional[str] = Field(None, min_length=4, description="Partition description")
    status: PartitionDbStatus