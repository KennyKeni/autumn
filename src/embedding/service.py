import os
import tempfile
from typing import List

import aiofiles
from fastapi import HTTPException
from llama_index.core import (
    Document,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import AsyncQdrantClient, QdrantClient
from types_aiobotocore_s3 import S3Client

from src.dependencies import QdrantDep, S3ClientDep
from src.files.repository import FileSqlRepository
from src.partitions.models.partition_files import PartitionFile


class EmbeddingService:
    def __init__(self, file_repository: FileSqlRepository):
        self.file_repository = file_repository

    async def embed_file(
        self,
        partition_file: PartitionFile,
        embed_model: OpenAILikeEmbedding,
        qdrant_client: AsyncQdrantClient,
        qdrant_sync_client: QdrantClient,
        s3_client: S3Client,
    ) -> VectorStoreIndex:
        if not partition_file.file or not partition_file.partition:
            raise ValueError("PartitionFile must have file and partition relationships loaded")

        documents: List[Document] = await self._get_documents(
            partition_file, s3_client
        )
        nodes: List[BaseNode] = await self._get_nodes_from_documents(documents)

        vector_store = QdrantVectorStore(
            client=qdrant_sync_client,
            aclient=qdrant_client,
            collection_name=str(partition_file.partition.collection_id),
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        vector_index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=False,
            use_async=True,
        )

        return vector_index

    async def _get_documents(
        self, partition_file: PartitionFile, s3_client: S3ClientDep
    ) -> List[Document]:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, str(partition_file.file.id))

            async with aiofiles.open(file_path, "wb") as temp_file:
                try:
                    response = await s3_client.get_object(
                        Bucket=partition_file.file.bucket_name, Key=partition_file.file.object_key
                    )

                    async for chunk in response["Body"].iter_chunks(chunk_size=8192):
                        await temp_file.write(chunk)

                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to download file from R2: {str(e)}",
                    )

            documents: list[Document] = SimpleDirectoryReader(
                input_files=[file_path], encoding="utf-8", errors="replace"
            ).load_data()

        for document in documents:
            document.metadata.update(
                {
                    "file_name": partition_file.file.name,
                    "file_id": partition_file.file.id,
                    "file_mime_type": partition_file.file.mime_type,
                    "partition_id": partition_file.partition.id,
                }
            )

        return documents

    async def _get_nodes_from_documents(
        self, documents: List[Document]
    ) -> List[BaseNode]:
        splitter = SentenceSplitter(chunk_size=1024)

        nodes = await splitter.aget_nodes_from_documents(documents)

        return nodes
