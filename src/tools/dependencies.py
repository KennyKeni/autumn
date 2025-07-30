from typing import Annotated

from fastapi import Depends
from src.embedding.dependencies import EmbeddingServiceDep, StorageContextDep, ToolStorageContextDep
from src.partitions.dependencies import PartitionFileToolRepositoryDep
from src.tools.service import ToolService


def _get_tool_service(
    partition_file_tool_repository: PartitionFileToolRepositoryDep,
    storage_context: StorageContextDep,
    tool_storage_context: ToolStorageContextDep,
    embedding_service: EmbeddingServiceDep
) -> ToolService:
    return ToolService(
        partition_file_tool_repository=partition_file_tool_repository,
        storage_context=storage_context,
        tool_storage_context=tool_storage_context,
        embedding_service=embedding_service,
    )

ToolServiceDep = Annotated[ToolService, Depends(_get_tool_service)]