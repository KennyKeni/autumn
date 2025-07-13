from typing import Annotated

from fastapi import Depends
from src.dependencies import PostgresDep
from src.partitions.repository import PartitionSqlRepository
from src.partitions.service import PartitionService


def _get_partition_repository(postgres_dep: PostgresDep) -> PartitionSqlRepository:
    return PartitionSqlRepository(postgres_dep)


PartitionRepositoryDep = Annotated[
    PartitionSqlRepository, Depends(_get_partition_repository)
]


def _get_partition_service(
    partition_repository: PartitionRepositoryDep,
) -> PartitionService:
    return PartitionService(partition_repository)

PartitionServiceDep = Annotated[PartitionService, Depends(_get_partition_service)]