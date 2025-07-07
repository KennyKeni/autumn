import tempfile
import os
from typing import List, Optional
from fastapi import HTTPException, UploadFile
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

from src.dependencies import PostgresDep, QdrantDep, S3ClientDep
from src.embedding.schemas.requests import EmbedFileRequest
from src.files.models.file import File
from src.files.repository import FileRepository
from src.files.exceptions import FileNotFoundError

class EmbeddingService:
    def __init__(self, file_repository: FileRepository):
        self.file_repository = file_repository

    async def embed_file(
        self,
        embed_file_request: EmbedFileRequest,
        embed_model: OpenAILikeEmbedding,
        qdrant_client: QdrantDep,
        s3_client: S3ClientDep,
        postgres_session: PostgresDep,
    ) -> VectorStoreIndex:
        file: Optional[File] = await self.file_repository.get_by_id(embed_file_request.file_id)
        if file is None:
            raise FileNotFoundError(embed_file_request.file_id)

        collection_name: str = embed_file_request.collection_name
        file_name: str = file.file_name

        documents: List[Document] = await self._get_documents(
            file, file_name, s3_client
        )
        nodes: List[BaseNode] = await self._get_nodes_from_documents(documents)

        vector_store = QdrantVectorStore(
            aclient=qdrant_client,
            collection_name=collection_name,
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        vector_index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=False,
        )

        return vector_index

    async def _get_documents(
        self, file: File, file_name: str, s3_client: S3ClientDep
    ) -> List[Document]:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file_name)

            with open(file_path, "wb") as temp_file:
                try:
                    response = await s3_client.get_object(
                        Bucket=file.bucket_name, Key=file.object_key
                    )

                    async for chunk in response["Body"].iter_chunks(chunk_size=8192):
                        temp_file.write(chunk)

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
                    "file_id": file.id,
                    "file_mime_type": file.mime_type,
                }
            )

        return documents

    async def _get_nodes_from_documents(
        self, documents: List[Document]
    ) -> List[BaseNode]:
        splitter = SentenceSplitter(chunk_size=1024)

        nodes = await splitter.aget_nodes_from_documents(documents)

        return nodes
