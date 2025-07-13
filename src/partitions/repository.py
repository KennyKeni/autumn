
from sqlalchemy.ext.asyncio import AsyncSession

from src.partitions.constants import PartitionDbStatus
from src.partitions.models.partition import Partition
from src.partitions.models.repository import PartitionCreate, PartitionUpdate
from src.repository import SqlRepository


class PartitionSqlRepository(SqlRepository[Partition, PartitionCreate, PartitionUpdate]):
    def __init__(self, postgres_session: AsyncSession):
        super().__init__(
            postgres_session,
            Partition,
            Partition.status != PartitionDbStatus.DELETED,
        )