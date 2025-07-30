from typing import Any, List, Optional, Sequence, Union
from llama_index.core import StorageContext, SummaryIndex, VectorStoreIndex
from llama_index.core.objects import ObjectIndex, ObjectRetriever
from llama_index.core.schema import BaseNode
from llama_index.core.tools import BaseTool
from llama_index.llms.openai_like import OpenAILike
from src.embedding.config import EMBEDDING_SETTINGS
from src.embedding.service import EmbeddingService
from src.embedding.utils import create_partition_filter, create_summary_tool_with_id, create_tool_group_filter
from src.partitions.constants import PartitionFileToolType
from src.partitions.models.partition import Partition
from src.partitions.models.partition_file import PartitionFile
from src.partitions.models.partition_file_tool import PartitionFileTool
from src.partitions.models.repository import PartitionFileToolCreate
from src.partitions.repository import PartitionFileToolSqlRepository
from src.tools.tool_handler import FileToolTypeHandler


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

            await self._create_file_tool_index(
                partition_file_tool=partition_file_tool,
                tool_storage_context=self.tool_storage_context,
                nodes=nodes,
            )

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
        vector_index = VectorStoreIndex.from_vector_store( # pyright: ignore[reportUnknownMemberType]
            vector_store=self.storage_context.vector_store,
            embed_model=self.embedding_service.embed_model, # TODO: Fix this bandaid
        )
        for partition_file in partition_files:
            for partition_file_tool in partition_file.partition_file_tools:
                handler = FileToolTypeHandler.get_handler(partition_file_tool.tool_type)
                tools.append(
                    handler.create_tool(
                        partition_file_tool=partition_file_tool, 
                        llm=llm,
                        storage_context=self.storage_context, 
                        vector_store_index=vector_index
                    )
                )

        return tools


    async def get_object_retriever(
        self,
        tool_group: str,
        partition: Partition,
        tools: List[BaseTool],
        **kwargs: Any,
    ) :
        object_index: ObjectIndex[VectorStoreIndex] = await self.embedding_service.get_object_index(tools, self.tool_storage_context, **kwargs)
        object_retriever: ObjectRetriever[Any] = object_index.as_retriever( # type: ignore[misc]
            similarity_top_k=5,
            vector_store_kwargs={
                "filter": {
                    "must": [
                        create_partition_filter(str(partition.id)),
                        create_tool_group_filter(tool_group)
                    ]
                }
            }
        )
        return object_retriever


    async def _create_file_tool_index(
        self,
        partition_file_tool: PartitionFileTool,
        tool_storage_context: StorageContext,
        nodes: Sequence[BaseNode],
    ) -> Optional[Union[SummaryIndex, VectorStoreIndex]]:
        """Create necessary index based on PartitionFileTool

        Args:
            partition_file_tool (PartitionFileTool): _description_
            tool_storage_context (StorageContext): _description_
            nodes (Sequence[BaseNode]): _description_

        Returns:
            Optional[BaseIndex]: _description_
        """
        tool_type = partition_file_tool.tool_type

        index = None

        # TODO Make a resolver for this instead
        match tool_type:
            case PartitionFileToolType.VECTOR:
                # No index needed
                pass
            case PartitionFileToolType.SUMMARY:
                index = create_summary_tool_with_id(
                    nodes=nodes,
                    storage_context=tool_storage_context,
                    index_id=str(partition_file_tool.id),
                )


        return index