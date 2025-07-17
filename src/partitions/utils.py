import select
from typing import Union
import uuid
from sqlalchemy import Select, select
from src.partitions.models.partition import Partition
from src.partitions.models.partition_files import PartitionFile
from src.partitions.models.repository import PartitionCreate
from src.partitions.schemas.request import CreatePartitionRequest
from src.partitions.schemas.response import PartitionResponse


class PartitionMapper:
    @staticmethod
    def db_to_response(partition: Partition) -> PartitionResponse:
        """Convert Partition SQLAlchemy model to response model"""
        return PartitionResponse.model_validate(partition)
    
    @staticmethod
    def to_partition_create(request: CreatePartitionRequest) -> PartitionCreate:
        return PartitionCreate(**request.model_dump(exclude_unset=True))
    
def partition_file_exist_stmt(partition_id: uuid.UUID, file_id: uuid.UUID) -> Select:
    return select(PartitionFile).where(PartitionFile.partition_id == partition_id).where(PartitionFile.file_id == file_id)