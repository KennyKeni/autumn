from typing import Any, List, Optional

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.objects import ObjectIndex, ObjectRetriever
from llama_index.core.schema import BaseNode
from llama_index.core.tools import BaseTool
from llama_index.llms.openai_like import OpenAILike

from src.embedding.config import EMBEDDING_SETTINGS
from src.embedding.service import EmbeddingService
from src.embedding.utils import create_partition_filter, create_tool_group_filter
from src.partitions.models.partition import Partition
from src.partitions.models.partition_file import PartitionFile
from src.partitions.models.partition_file_tool import PartitionFileTool
from src.partitions.models.repository import PartitionFileToolCreate
from src.partitions.repository import PartitionFileToolSqlRepository
from src.tools.tool_handler import FileToolTypeHandler
from src.tools.utils import get_partition_file_llamaindex_filter


class ToolService:
    def __init__(
        self,
        partition_file_tool_repository: PartitionFileToolSqlRepository,
        storage_context: StorageContext,
        tool_storage_context: StorageContext,
        embedding_service: EmbeddingService,
    ):
        self.partition_file_tool_repository = partition_file_tool_repository
        self.storage_context = storage_context
        self.tool_storage_context = tool_storage_context
        self.embedding_service = embedding_service

    async def create_default_tools(
        self,
        partition_file: PartitionFile,
        nodes: List[BaseNode],
    ) -> List[PartitionFileTool]:
        tools: List[PartitionFileTool] = []

        for tool_type in EMBEDDING_SETTINGS.DEFAULT_FILE_TOOLS:
            partition_file_tool: PartitionFileTool = (
                await self.partition_file_tool_repository.create(
                    PartitionFileToolCreate(
                        partition_file=partition_file,
                        partition_file_id=partition_file.id,
                        tool_type=tool_type,
                        tool_group=EMBEDDING_SETTINGS.DEFAULT_FILE_TOOL_GROUP,
                    )
                )
            )

            await self.partition_file_tool_repository.session.flush()

            tools.append(partition_file_tool)

            await self.embedding_service.embed_tool(
                partition_file_tool=partition_file_tool,
                tool_storage_context=self.tool_storage_context,
            )

        return tools

    async def get_file_tools(
        self,
        partition_files: List[PartitionFile],
        llm: OpenAILike,
    ) -> List[BaseTool]:
        tools: List[BaseTool] = []
        vector_index = VectorStoreIndex.from_vector_store(  # pyright: ignore[reportUnknownMemberType]
            vector_store=self.storage_context.vector_store,
            embed_model=self.embedding_service.embed_model,  # TODO: Fix this bandaid
        )
        for partition_file in partition_files:
            nodes: Optional[List[BaseNode]] = None
            for partition_file_tool in partition_file.partition_file_tools:
                handler = FileToolTypeHandler.get_handler(partition_file_tool.tool_type)
                if handler.requiresFileNode and nodes == None:
                    # TODO Switch to native qdrant
                    metadata_filter = get_partition_file_llamaindex_filter(str(partition_file_tool.partition_file_id))
                    nodes = await self.storage_context.vector_store.aget_nodes(
                        node_ids=None, filters=metadata_filter
                    )

                tools.append(
                    await handler.create_tool(
                        partition_file_tool=partition_file_tool,
                        llm=llm,
                        storage_context=self.storage_context,
                        vector_store_index=vector_index,
                        nodes=nodes
                    )
                )

        return tools

    async def get_object_retriever(
        self,
        tool_group: str,
        partition: Partition,
        tools: List[BaseTool],
        **kwargs: Any,
    ):
        object_index: ObjectIndex[VectorStoreIndex] = (
            await self.embedding_service.get_object_index(
                tools, self.tool_storage_context, **kwargs
            )
        )
        object_retriever: ObjectRetriever[Any] = object_index.as_retriever(  # type: ignore[misc]
            similarity_top_k=5,
            vector_store_kwargs={
                "filter": {
                    "must": [
                        create_partition_filter(str(partition.id)),
                        create_tool_group_filter(tool_group),
                    ]
                }
            },
        )
        return object_retriever
