from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypedDict, Unpack

from llama_index.core import StorageContext, SummaryIndex, VectorStoreIndex
from llama_index.core.indices.base import BaseIndex
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.tools import BaseTool, FunctionTool, QueryEngineTool
from llama_index.core.vector_stores import FilterOperator, MetadataFilter, MetadataFilters
from llama_index.llms.openai_like import ( # pyright: ignore[reportMissingTypeStubs]
    OpenAILike,
)
from pydantic import BaseModel

from src.embedding.utils import create_file_filter, create_partition_filter
from src.partitions.constants import PartitionFileToolType
from src.partitions.models.partition_file_tool import PartitionFileTool
from src.utils import set_instance_var


class CreateToolArgs(TypedDict):
    vector_store_index: VectorStoreIndex
    storage_context: StorageContext


class FileToolHelper(ABC):
    @staticmethod
    def _create_tool_name(tool_type: PartitionFileToolType, file_name: str) -> str:
        # Tool type name normalization
        normalized_tool = "_".join(tool_type.split(" "))

        # Handle file name and potentially no extension
        name_parts = file_name.split(".")
        if len(name_parts) > 1:
            processed_file = "_".join(name_parts[:-1]).replace(" ", "_")
        else:
            processed_file = file_name.replace(" ", "_")  # No extension

        return f"{normalized_tool}_tool_{processed_file}"

    @staticmethod
    @abstractmethod
    def create_tool_description(file_name: str) -> str:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_signature(cls) -> type[BaseModel]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    async def create_tool(
        cls,
        partition_file_tool: PartitionFileTool,
        llm: OpenAILike,
        **kwargs: Unpack[CreateToolArgs],
    ) -> BaseTool:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def create_tool_name(cls, file_name: str) -> str:
        raise NotImplementedError()


class SummaryToolHandler(FileToolHelper):
    class SummaryQueryArgs(BaseModel):
        query: str

    index_type: PartitionFileToolType = PartitionFileToolType.SUMMARY

    @staticmethod
    def create_tool_description(file_name: str) -> str:
        return (
            f"Search for specific concepts, methods, techniques, or technical details in {file_name.split('.')[0]}. "
            f"Use this for questions about specific algorithms, implementations, formulas, or technical concepts. "
            f"Examples: quantization methods, model architectures, specific equations."
        )

    @classmethod
    def create_tool_name(cls, file_name: str) -> str:
        return cls._create_tool_name(cls.index_type, file_name)

    @classmethod
    def get_signature(cls) -> type[BaseModel]:
        return cls.SummaryQueryArgs

    @classmethod
    async def create_tool(
        cls,
        partition_file_tool: PartitionFileTool,
        llm: OpenAILike,
        **kwargs: Unpack[CreateToolArgs],
    ) -> BaseTool:
        # TODO Switch to qdrant client
        metadata_filter = MetadataFilters(
            filters=[
                MetadataFilter(
                    key="partition_file_id",
                    value=str(partition_file_tool.partition_file_id),
                    operator=FilterOperator.EQ,
                )
            ]
        )

        storage_context = kwargs["storage_context"]

        nodes = await storage_context.vector_store.aget_nodes(
            node_ids=None, filters=metadata_filter
        )

        summary_index: BaseIndex[Any] = SummaryIndex(
            nodes=nodes
        )  # pyright: ignore[reportUnknownVariableType]
        summary_query_engine: BaseQueryEngine = (
            summary_index.as_query_engine(  # pyright: ignore[reportUnknownMemberType]
                response_mode="tree_summarize",
                use_async=True,
                llm=llm,
            )
        )

        summary_tool = QueryEngineTool.from_defaults(
            name=cls.create_tool_name(partition_file_tool.partition_file.file.name),
            query_engine=summary_query_engine,
            description=cls.create_tool_description(
                partition_file_tool.partition_file.file.name
            ),
        )

        set_instance_var(summary_tool, "id", str(partition_file_tool.id))

        return summary_tool


class VectorToolHandler(FileToolHelper):
    class VectorQueryArgs(BaseModel):
        query: str

    index_type: PartitionFileToolType = PartitionFileToolType.VECTOR

    @staticmethod
    def create_tool_description(file_name: str) -> str:
        return (
            f"Search for specific concepts, methods, techniques, or technical details in {file_name.split('.')[0]}. "
            f"Use this for questions about specific algorithms, implementations, formulas, or technical concepts. "
            f"Examples: quantization methods, model architectures, specific equations."
        )

    @classmethod
    def get_signature(cls) -> type[BaseModel]:
        return cls.VectorQueryArgs

    @classmethod
    def create_tool_name(cls, file_name: str) -> str:
        return cls._create_tool_name(cls.index_type, file_name)

    @classmethod
    async def create_tool(
        cls,
        partition_file_tool: PartitionFileTool,
        llm: OpenAILike,
        **kwargs: Unpack[CreateToolArgs],
    ) -> BaseTool:

        vector_index: VectorStoreIndex = kwargs["vector_store_index"]

        async def vector_query(
            query: str,
        ):
            """Use to answer questions over a given paper.

            Useful if you have specific questions over the paper.

            Args:
                query (str): the string query to be embedded.

            """
            qdrant_filter = {
                "must": [
                    create_file_filter(str(partition_file_tool.partition_file.file_id)),
                    create_partition_filter(
                        str(partition_file_tool.partition_file.partition_id)
                    ),
                ]
            }

            query_engine = vector_index.as_query_engine(  # pyright: ignore[reportUnknownMemberType]
                similarity_top_k=5,  # TODO Add to config
                vector_store_kwargs={"filter": qdrant_filter},
                use_async=True,
                llm=llm,
            )
            response = await query_engine.aquery(query)
            return response

        vector_query_tool = FunctionTool.from_defaults(
            name=cls.create_tool_name(partition_file_tool.partition_file.file.name),
            fn=vector_query,
            description=cls.create_tool_description(
                partition_file_tool.partition_file.file.name
            ),
        )

        set_instance_var(vector_query_tool, "id", str(partition_file_tool.id))

        return vector_query_tool


class FileToolTypeHandler:
    handlers: Dict[PartitionFileToolType, Type[FileToolHelper]] = {
        PartitionFileToolType.SUMMARY: SummaryToolHandler,
        PartitionFileToolType.VECTOR: VectorToolHandler,
    }

    @classmethod
    def get_handler(
        cls, partition_tool_type: PartitionFileToolType
    ) -> type[FileToolHelper]:
        """Gets FileTool helper methods

        Args:
            partition_tool_type (PartitionFileToolType): _description_

        Returns:
            type[FileToolHelper]: _description_
        """
        return cls.handlers[partition_tool_type]
