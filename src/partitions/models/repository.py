import uuid
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from src.exceptions import ValidationMatchHTTPException
from src.partitions.constants import PartitionDbStatus, PartitionFileToolType

from src.partitions.models.partition import Partition
from src.files.models.file import File
from src.partitions.models.partition_file import PartitionFile


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


# String annotations due to circular improt
class PartitionFileCreate(BaseModel):
    partition_id: uuid.UUID
    file_id: uuid.UUID
    partition: Optional["Partition"] = None
    file: Optional["File"] = None
    
    @model_validator(mode='after')
    def validate_ids_match(self):
        if self.partition and self.partition.id != self.partition_id:
            raise ValidationMatchHTTPException(Partition)
        if self.file and self.file.id != self.file_id:
            raise ValidationMatchHTTPException(File)
        return self


class PartitionFileUpdate(BaseModel):
    pass


class PartitionFileToolCreate(BaseModel):
    tool_group: str
    tool_type: PartitionFileToolType
    partition_file_id: uuid.UUID
    partition_file: Optional["PartitionFile"] = None

    @model_validator(mode='after')
    def validate_ids_match(self):
        if self.partition_file and self.partition_file.id != self.partition_file_id:
            raise ValidationMatchHTTPException(PartitionFile)
        
        return self


class PartitionFileToolUpdate(BaseModel):
    tool_group: str