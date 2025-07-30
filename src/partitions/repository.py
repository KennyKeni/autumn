import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.partitions.constants import PartitionDbStatus
from src.partitions.models.partition import Partition
from src.partitions.models.partition_file import PartitionFile
from src.partitions.models.partition_file_tool import PartitionFileTool
from src.partitions.models.repository import (PartitionCreate,
                                              PartitionFileCreate,
                                              PartitionFileToolCreate,
                                              PartitionFileToolUpdate,
                                              PartitionFileUpdate,
                                              PartitionUpdate)
from src.repository import SqlRepository


class PartitionSqlRepository(
    SqlRepository[Partition, PartitionCreate, PartitionUpdate]
):
    def __init__(self, postgres_session: AsyncSession) -> None:
        super().__init__(
            postgres_session,
            Partition,
            Partition.status != PartitionDbStatus.DELETED,
        )


class PartitionFileSqlRepository(
    SqlRepository[PartitionFile, PartitionFileCreate, PartitionFileUpdate]
):
    def __init__(self, postgres_session: AsyncSession) -> None:
        super().__init__(
            postgres_session,
            PartitionFile,
        )

    async def get_partition_file_from_fk(
        self, partition_id: uuid.UUID, file_id: uuid.UUID
    ) -> Optional[PartitionFile]:
        return await self._get_one(
            PartitionFile.partition_id == partition_id, PartitionFile.file_id == file_id
        )


class PartitionFileToolSqlRepository(
    SqlRepository[PartitionFileTool, PartitionFileToolCreate, PartitionFileToolUpdate]
):
    def __init__(self, postgres_session: AsyncSession) -> None:
        super().__init__(
            postgres_session,
            PartitionFileTool,
        )
