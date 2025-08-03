import uuid
from typing import Any, Dict, Optional, Sequence, Union

from llama_index.core import StorageContext, SummaryIndex, VectorStoreIndex
from llama_index.core.data_structs import IndexList
from llama_index.core.embeddings.utils import (
    EmbedType, # pyright: ignore[reportUnknownVariableType]
)
from llama_index.core.objects import ObjectIndex
from llama_index.core.schema import BaseNode, IndexNode
from llama_index.core.tools import BaseTool
from llama_index.core.vector_stores.types import BasePydanticVectorStore

from src.llamaindex_patch.node_mapping.id_tool_mapping import IdToolMapping


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
