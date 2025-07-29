import os
import tempfile
from typing import List, Optional, Sequence, Union

import aiofiles
from fastapi import HTTPException
from llama_index.core import (Document, SimpleDirectoryReader, StorageContext,
                              SummaryIndex, VectorStoreIndex)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode, TextNode
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from types_aiobotocore_s3 import S3Client

from src.embedding.config import EMBEDDING_SETTINGS
from src.embedding.utils import (FileToolTypeHandler,
                                 create_summary_tool_with_id, create_tool_name,
                                 create_tool_node_with_id)
from src.partitions.constants import PartitionFileToolType
from src.partitions.models.partition_file import PartitionFile
from src.partitions.models.partition_file_tool import PartitionFileTool
from src.partitions.models.repository import PartitionFileToolCreate
from src.partitions.repository import PartitionFileToolSqlRepository


class EmbeddingService:
    def __init__(
        self, 
        partition_file_tool_repository: PartitionFileToolSqlRepository,
        storage_context: StorageContext,
        tool_storage_context: StorageContext,
        # file_repository: FileSqlRepository,
    ) -> None:
        self.partition_file_tool_repository = partition_file_tool_repository
        self.storage_context = storage_context
        self.tool_storage_context = tool_storage_context
        # self.file_repository = file_repository

    async def embed_file(
        self,
        partition_file: PartitionFile,
        embed_model: OpenAILikeEmbedding,
        s3_client: S3Client,
    ) -> List[PartitionFileTool]:
        if not partition_file.file or not partition_file.partition:
            raise ValueError("PartitionFile must have file and partition relationships loaded")

        documents: List[Document] = await self._get_documents(
            partition_file, s3_client
        )
        nodes: List[BaseNode] = await self._get_nodes_from_documents(documents)

        vector_store = self.storage_context.vector_store

        vector_index = VectorStoreIndex.from_vector_store( # pyright: ignore[reportUnknownMemberType]
            vector_store=vector_store,
            embed_model=embed_model,
        )

        await vector_index.ainsert_nodes(nodes)

        tools: List[PartitionFileTool] = []

        for tool_type in EMBEDDING_SETTINGS.DEFAULT_FILE_TOOLS:
            partition_file_tool: PartitionFileTool = await self.partition_file_tool_repository.create(
                PartitionFileToolCreate(
                    partition_file=partition_file,
                    partition_file_id=partition_file.id,
                    tool_type=tool_type,
                    tool_group=EMBEDDING_SETTINGS.DEFAULT_FILE_TOOL_GROUP,
                )
            )

            await self.partition_file_tool_repository.session.flush()

            tools.append(partition_file_tool)

            await self.create_file_tool_index(
                partition_file_tool=partition_file_tool,
                tool_storage_context=self.tool_storage_context,
                nodes=nodes,
            )

            await self.embed_tool(
                partition_file_tool=partition_file_tool,
                tool_storage_context=self.tool_storage_context,
            )

        return tools

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
            file_path = os.path.join(temp_dir, str(partition_file.file.id) + partition_file.file.name)

            async with aiofiles.open(file_path, "wb") as temp_file:
                try:
                    response = await s3_client.get_object(
                        Bucket=partition_file.file.bucket_name, Key=partition_file.file.object_key
                    )

                    async for chunk in response["Body"].iter_chunks(chunk_size=64*1024): # 64 * kb
                        await temp_file.write(chunk)

                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to download file from R2: {str(e)}",
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
                    "file_id": str(partition_file.file_id), # Deletion by file_id
                    "partition_id": str(partition_file.partition_id), # Deletion by partition_id
                    "partition_file_id": str(partition_file.id) # Deletion by partition_file_id
                }
            )
            exclude_keys = ["file_id", "partition_id", "partition_file_id", "file_mime_type"]
            document.excluded_embed_metadata_keys.extend(exclude_keys)
            document.excluded_llm_metadata_keys.extend(exclude_keys)

        return documents

    async def _get_nodes_from_documents(
        self, documents: List[Document]
    ) -> List[BaseNode]:
        """Generates llamaindex nodes from documents

        Args:
            documents (List[Document]): _description_

        Returns:
            List[BaseNode]: _description_
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
        signature = FileToolTypeHandler.get_signature(tool_type)

        # Add to handler map
        tool_name = create_tool_name(tool_type, file_name)
        
        tool_node: TextNode = create_tool_node_with_id(
            tool_name=tool_name,
            tool_description=handler.create_tool_description(file_name),
            tool_schema=signature,
            tool_identity=partition_file_tool.id,
            partition_id=partition_file_tool.partition_file.partition_id,
            partition_file_id=partition_file_tool.partition_file.id,
        )

        tool_node.metadata = {
            "name": tool_name,
            "file_id": str(partition_file_tool.partition_file.file_id), # Deletion by file_id
            "partition_id": str(partition_file_tool.partition_file.partition_id), # Deletion by partition_id
            "partition_file_id": str(partition_file_tool.partition_file_id), # Deletion by partition_file_id
            "partition_file_tool_id": str(partition_file_tool.id),
        }
        exclude_keys = ["file_id", "partition_id", "partition_file_id", "file_mime_type"]
        tool_node.excluded_embed_metadata_keys.extend(exclude_keys)
        tool_node.excluded_llm_metadata_keys.extend(exclude_keys)


        vector_index = VectorStoreIndex.from_vector_store(tool_storage_context.vector_store) # pyright: ignore[reportUnknownMemberType]
        await vector_index.ainsert_nodes([tool_node])

        return tool_node

    async def create_file_tool_index(
        self,
        partition_file_tool: PartitionFileTool,
        tool_storage_context: StorageContext,
        nodes: Sequence[BaseNode]
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
                    index_id=partition_file_tool.id,
                    nodes=nodes,
                    storage_context=tool_storage_context
                )

        return index

