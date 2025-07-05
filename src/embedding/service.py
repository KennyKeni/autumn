import tempfile
import os
from typing import List
from fastapi import UploadFile
from llama_index.core import Document, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from llama_index.core.schema import BaseNode
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore

from src.dependencies import QdrantDep
from src.embedding.schemas.requests import EmbedFileRequest


class EmbeddingService:
    def __init__(self):
        pass

    async def embed_file(self, qdrant_client: QdrantDep, embed_model: OpenAILikeEmbedding, embed_file_request: EmbedFileRequest) -> VectorStoreIndex:
        file: UploadFile = embed_file_request.file
        collection_name: str = embed_file_request.collection_name
        file_name: str = file.filename or collection_name
        
        documents: List[Document] = await self._get_documents(file, file_name)
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
    

    async def _get_documents(self, file: UploadFile, file_name: str) -> List[Document]:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, file_name)

            with open(file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            documents = SimpleDirectoryReader(
                input_files=[file_path],
                encoding="utf-8",
                errors="replace"
            ).load_data()

        return documents    
    
    async def _get_nodes_from_documents(self, documents: List[Document]) -> List[BaseNode]:
        splitter = SentenceSplitter(chunk_size=1024)

        nodes = await splitter.aget_nodes_from_documents(documents)
        # for node in nodes:
        #     current_content = node.get_content()
        #     cleaned_content = current_content.encode('utf-8', 'surrogatepass').decode('utf-8', 'replace')
        #     node.set_content(cleaned_content)

        return nodes