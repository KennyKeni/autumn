from typing import Optional
import uuid

from pydantic import BaseModel, Field

from src.partitions.constants import PartitionDbStatus


class PartitionCreate(BaseModel):
    name: str = Field(..., min_length=4, description="Partition name")
    description: Optional[str] = Field(None, min_length=4, description="Partition description")
    collection_id: uuid.UUID
    status: PartitionDbStatus = Field(
        description="", default=PartitionDbStatus.ACTIVE)

class PartitionUpdate(BaseModel):
    name: str = Field(..., min_length=4, description="Partition name")  
    description: Optional[str] = Field(None, min_length=4, description="Partition description")
    status: PartitionDbStatus