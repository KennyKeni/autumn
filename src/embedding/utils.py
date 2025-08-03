import uuid
from typing import Any, Dict, Optional, Sequence, Type, Union

from llama_index.core import StorageContext, SummaryIndex, VectorStoreIndex
from llama_index.core.data_structs import IndexList
from llama_index.core.embeddings.utils import EmbedType # pyright: ignore[reportUnknownVariableType]
from llama_index.core.objects import ObjectIndex
from llama_index.core.objects.base_node_mapping import BaseObjectNodeMapping
from llama_index.core.schema import BaseNode, IndexNode, TextNode
from llama_index.core.tools import BaseTool
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from pydantic import BaseModel

from src.utils import get_instance_var


def create_summary_tool_with_id(
    index_id: Union[uuid.UUID, str],
    nodes: Optional[Sequence[BaseNode]] = None,
    objects: Optional[Sequence[IndexNode]] = None,
    storage_context: Optional[StorageContext] = None,
    show_progress: bool = False,
    **kwargs: Any,
) -> SummaryIndex:
    """
    Create a summary index with a predefined id
    """
    index_id = str(index_id)
    index_struct = IndexList(index_id=index_id)
    for node in nodes or []:
        index_struct.add_node(node)

    return SummaryIndex(
        objects=objects,
        index_struct=index_struct,
        show_progress=show_progress,
        storage_context=storage_context,
        **kwargs,
    )


def create_tool_node_with_id(
    tool_name: str,
    tool_description: str,
    tool_schema: Optional[Type[BaseModel]],
    tool_identity: Union[uuid.UUID, str],
    tool_group: str,
    partition_id: Union[uuid.UUID, str],
    partition_file_id: Optional[Union[uuid.UUID, str]] = None,
):
    """Function convert Tool to node."""
    partition_id_str = str(partition_id)
    partition_file_id_str = str(partition_file_id) if partition_file_id else None
    tool_identity_str = str(tool_identity)

    node_text = f"Tool name: {tool_name}\n" f"Tool description: {tool_description}\n"
    if tool_schema is not None:
        schema_dict = tool_schema.model_json_schema()
        schema_dict["title"] = tool_name
        node_text += f"Tool schema: {tool_schema.model_json_schema()}\n"

    return TextNode(
        id_=tool_identity_str,
        text=node_text,
        metadata={
            "name": tool_name,
            "partition_id": partition_id_str,
            "partition_file_id": partition_file_id_str,
            "tool_group": tool_group,
        },
        excluded_embed_metadata_keys=[
            "name",
            "partition_file_id_str",
            "partition_file_id",
            "tool_group",
        ],
        excluded_llm_metadata_keys=[
            "name",
            "partition_file_id_str",
            "partition_file_id",
            "tool_group",
        ],
    )


# def create_tool_node_uuid5(
#         partition_id: str,
#         tool_name: str,
#         tool_description: str,
#         tool_schema: Optional[Type[BaseModel]] = None,
#     ):
#     """Function convert Tool to node."""
#     tool_identity_string = (
#         f"{tool_name}{tool_description}{tool_schema}{partition_id}"
#     )
#     tool_identity = uuid.uuid5(uuid.NAMESPACE_DNS, tool_identity_string)
#     return create_tool_node_with_id(tool_name, tool_description, tool_schema, tool_identity)


class IdToolMapping(BaseObjectNodeMapping[Any]):
    """Custom tool mapping that is used to sync Postgres
    PartitionFileTool to Qdrant.

    Args:
        BaseObjectNodeMapping (Generic[OT]): Base Llamaindex Class
    """

    def __init__(self, objs: Optional[Sequence[BaseTool]] = None) -> None:
        objs = objs or []
        try:
            self._tools: Dict[str, BaseTool] = {
                get_instance_var(tool, "id", str): tool for tool in objs
            }
        except AttributeError as e:
            raise Exception(f"Tool missing 'id' attribute: {e}")

    @classmethod
    def from_objects(
        cls, objs: Sequence[BaseTool], *args: Any, **kwargs: Any
    ) -> "BaseObjectNodeMapping[Any]":
        return cls(objs)

    def _add_object(self, obj: BaseTool) -> None:
        try:
            self._tools[get_instance_var(obj, "id", str)] = obj
        except AttributeError as e:
            raise Exception(f"Tool missing 'id' attribute: {e}")

    def to_node(self, obj: BaseTool) -> TextNode:
        """To node."""
        raise NotImplementedError("Class was not intended for this use")

    def _from_node(self, node: BaseNode) -> BaseTool:
        """From node."""
        return self._tools[node.node_id]


def get_object_index(
    tools: Sequence[BaseTool],
    vector_store: BasePydanticVectorStore,
    embed_model: Optional[EmbedType],  # pyright: ignore[reportUnknownParameterType]
    **kwargs: Any,
) -> ObjectIndex[VectorStoreIndex]:
    id_tool_mapping = IdToolMapping(tools)
    vector_index: VectorStoreIndex = (
        VectorStoreIndex.from_vector_store(  # pyright: ignore[reportUnknownMemberType]
            vector_store=vector_store,
            embed_model=embed_model,
            **kwargs,
        )
    )

    return ObjectIndex[VectorStoreIndex](
        index=vector_index,
        object_node_mapping=id_tool_mapping,
    )


def create_file_filter(file_id: str) -> Dict[str, Any]:
    return create_qdrant_filter("file_id", file_id)


def create_partition_filter(partition_id: str) -> Dict[str, Any]:
    return create_qdrant_filter("partition_id", partition_id)


def create_tool_group_filter(tool_group: str) -> Dict[str, Any]:
    return create_qdrant_filter("tool_group", tool_group)


def create_qdrant_filter(key: str, value: str) -> Dict[str, Any]:
    return {"key": key, "match": {"value": value}}
