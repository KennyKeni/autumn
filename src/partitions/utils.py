from src.partitions.models.partition import Partition
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