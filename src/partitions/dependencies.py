from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.dependencies import PostgresDep
from src.factory import get_id_from_path_factory, validate_entity_exists_factory
from src.partitions.models.partition import Partition
from src.partitions.repository import (
    PartitionFileSqlRepository,
    PartitionFileToolSqlRepository,
    PartitionSqlRepository,
)
from src.partitions.service import PartitionService


# Repositories
def _get_partition_repository(session: PostgresDep) -> PartitionSqlRepository:
    return PartitionSqlRepository(session)


def _get_partition_file_repository(session: PostgresDep) -> PartitionFileSqlRepository:
    return PartitionFileSqlRepository(session)


def _get_partition_file_tool_repository(
    session: PostgresDep,
) -> PartitionFileToolSqlRepository:
    return PartitionFileToolSqlRepository(session)


# Entities
async def _get_partition_with_collection(
    session: PostgresDep,
    partition_id: UUID = Depends(get_id_from_path_factory("partition_id")),
) -> Partition | None:
    query = (
        select(Partition)
        .where(Partition.id == partition_id)
        .options(
            joinedload(Partition.collection),
            joinedload(Partition.partition_files),
        )
    )
    return await session.scalar(query)


# Service


def _get_partition_service(
    partition_repository: "PartitionRepositoryDep",
    partition_file_repository: "PartitionFileRepositoryDep",
) -> PartitionService:
    return PartitionService(partition_repository, partition_file_repository)


PartitionServiceDep = Annotated[PartitionService, Depends(_get_partition_service)]
PartitionRepositoryDep = Annotated[
    PartitionSqlRepository, Depends(_get_partition_repository)
]
PartitionFileRepositoryDep = Annotated[
    PartitionFileSqlRepository, Depends(_get_partition_file_repository)
]
PartitionFileToolRepositoryDep = Annotated[
    PartitionFileToolSqlRepository, Depends(_get_partition_file_tool_repository)
]
ValidPartitionLoadedDep = Annotated[Partition, Depends(_get_partition_with_collection)]
ValidPartitionDep = Annotated[
    Partition,
    Depends(
        validate_entity_exists_factory(
            Partition, _get_partition_repository, "partition_id"
        )
    ),
]
