import os
import tempfile
from typing import Any, List

import aiofiles
from fastapi import HTTPException
from llama_index.core import (Document, SimpleDirectoryReader, StorageContext,
                              VectorStoreIndex)
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.objects import ObjectIndex
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.tools import BaseTool

from types_aiobotocore_s3 import S3Client

from src.embedding.utils import IdToolMapping, create_tool_node_with_id
from src.partitions.models.partition_file import PartitionFile
from src.partitions.models.partition_file_tool import PartitionFileTool
from src.partitions.repository import PartitionFileToolSqlRepository
from src.tools.tool_handler import FileToolTypeHandler


class EmbeddingService:
    def __init__(
        self,
        embed_model: BaseEmbedding,
        partition_file_tool_repository: PartitionFileToolSqlRepository,
        storage_context: StorageContext,
    ) -> None:
        self.embed_model = embed_model
        self.partition_file_tool_repository = partition_file_tool_repository
        self.storage_context = storage_context

    async def embed_file(
        self,
        partition_file: PartitionFile,
        s3_client: S3Client,
    ) -> List[BaseNode]:
        if not partition_file.file or not partition_file.partition:
            raise ValueError(
                "PartitionFile must have file and partition relationships loaded"
            )

        documents: List[Document] = await self._get_documents(partition_file, s3_client)
        nodes: List[BaseNode] = await self._get_nodes_from_documents(documents)

        vector_index = VectorStoreIndex.from_vector_store(  # pyright: ignore[reportUnknownMemberType]
            vector_store=self.storage_context.vector_store,
            embed_model=self.embed_model,
        )

        await vector_index.ainsert_nodes(nodes)
        await self.storage_context.docstore.async_add_documents(nodes, allow_update=False)

        return nodes


    async def get_object_index(
        self,
        tools: List[BaseTool],
        tool_storage_context: StorageContext,
        **kwargs: Any,
    ) -> ObjectIndex[VectorStoreIndex]:
        id_tool_mapping = IdToolMapping(tools)
        vector_index = VectorStoreIndex.from_vector_store( # pyright: ignore[reportUnknownMemberType]
            vector_store=tool_storage_context.vector_store,
            embed_model=self.embed_model,
            **kwargs,
        )

        return ObjectIndex[VectorStoreIndex](
            index=vector_index,
            object_node_mapping=id_tool_mapping,
        )

    async def _get_documents(
        self, partition_file: PartitionFile, s3_client: S3Client
    ) -> List[Document]:
        """Generate llamaindex document via S3 file using temporary dir

        Args:
            partition_file (PartitionFile): _description_
            s3_client (S3Client): _description_

        Raises:
            HTTPException: _description_

        Returns:
            List[Document]: _description_
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(
                temp_dir, str(partition_file.file.id) + partition_file.file.name
            )

            async with aiofiles.open(file_path, "wb") as temp_file:
                try:
                    response = await s3_client.get_object(
                        Bucket=partition_file.file.bucket_name,
                        Key=partition_file.file.object_key,
                    )

                    async for chunk in response["Body"].iter_chunks(
                        chunk_size=64 * 1024
                    ):  # 64 * kb
                        await temp_file.write(chunk)

                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to download file from S3: {str(e)}",
                    )

            documents: list[Document] = SimpleDirectoryReader(
                input_files=[file_path],
                encoding="utf-8",
                num_files_limit=1,
            ).load_data()

        # Move this logic somewhere else
        for document in documents:
            document.doc_id = str(partition_file.id)
            document.metadata.update(
                {
                    "file_name": partition_file.file.name,
                    "file_mime_type": partition_file.file.mime_type,
                    "file_id": str(partition_file.file_id),  # Deletion by file_id
                    "partition_id": str(
                        partition_file.partition_id
                    ),  # Deletion by partition_id
                    "partition_file_id": str(
                        partition_file.id
                    ),  # Deletion by partition_file_id
                }
            )
            exclude_keys = [
                "file_id",
                "partition_id",
                "partition_file_id",
                "file_mime_type",
            ]
            document.excluded_embed_metadata_keys.extend(exclude_keys)
            document.excluded_llm_metadata_keys.extend(exclude_keys)

        return documents

    async def _get_nodes_from_documents(
        self, documents: List[Document]
    ) -> List[BaseNode]:
        """Generates llamaindex nodes from documents

        Args:
            documents (List[Document]): List of llamaindex doucment instances

        Returns:
            List[BaseNode]: List of basenodes
        """
        splitter = SentenceSplitter(chunk_size=1024)

        nodes = await splitter.aget_nodes_from_documents(documents)

        return nodes

    async def embed_tool(
        self,
        partition_file_tool: PartitionFileTool,
        tool_storage_context: StorageContext,
    ) -> TextNode:
        tool_type = partition_file_tool.tool_type
        file_name = partition_file_tool.partition_file.file.name

        handler = FileToolTypeHandler.get_handler(tool_type)

        # Add to handler map
        tool_name = handler.create_tool_name(file_name)

        tool_node: TextNode = create_tool_node_with_id(
            tool_name=tool_name,
            tool_description=handler.create_tool_description(file_name),
            tool_schema=handler.get_signature(),
            tool_identity=partition_file_tool.id,
            tool_group=partition_file_tool.tool_group,
            partition_id=partition_file_tool.partition_file.partition_id,
            partition_file_id=partition_file_tool.partition_file.id,
        )

        tool_node.metadata = {
            "name": tool_name,
            "file_id": str(
                partition_file_tool.partition_file.file_id
            ),  # Deletion by file_id
            "partition_id": str(
                partition_file_tool.partition_file.partition_id
            ),  # Deletion by partition_id
            "partition_file_id": str(
                partition_file_tool.partition_file_id
            ),  # Deletion by partition_file_id
            "partition_file_tool_id": str(partition_file_tool.id),
        }
        exclude_keys = [
            "file_id",
            "partition_id",
            "partition_file_id",
            "file_mime_type",
        ]
        tool_node.excluded_embed_metadata_keys.extend(exclude_keys)
        tool_node.excluded_llm_metadata_keys.extend(exclude_keys)

        vector_index = VectorStoreIndex.from_vector_store( # pyright: ignore[reportUnknownMemberType]
            vector_store=tool_storage_context.vector_store, embed_model=self.embed_model
        )
        await vector_index.ainsert_nodes([tool_node])

        return tool_node