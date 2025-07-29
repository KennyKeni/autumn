from typing import Annotated

from fastapi import Depends
from llama_index.core import StorageContext
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.storage.docstore.postgres import PostgresDocumentStore
from llama_index.storage.index_store.postgres import PostgresIndexStore
from llama_index.vector_stores.qdrant import QdrantVectorStore

from src.config import settings
from src.dependencies import QdrantDep, QdrantSyncDep
from src.embedding.config import EMBEDDING_SETTINGS
from src.embedding.service import EmbeddingService
from src.partitions.dependencies import (PartitionFileToolRepositoryDep,
                                         ValidPartitionDep,
                                         ValidPartitionLoadedDep)
from src.partitions.utils import get_tool_partition

# Only supports deepinfra for now, no point branching out currently
def _get_embed_model_v2(partition: ValidPartitionLoadedDep) -> OpenAILikeEmbedding:
    collection = partition.collection
    
    return OpenAILikeEmbedding(
        model_name=collection.embedding_model,
        api_base=EMBEDDING_SETTINGS.API_BASE,
        api_key=EMBEDDING_SETTINGS.API_KEY,
        api_version=EMBEDDING_SETTINGS.API_VERSION,
        embed_batch_size=EMBEDDING_SETTINGS.EMBED_BATCH_SIZE,
        max_retries=EMBEDDING_SETTINGS.MAX_RETIRES,
        timeout=EMBEDDING_SETTINGS.TIMEOUT,
        dimensions=collection.vector_dimension,
        reuse_client=EMBEDDING_SETTINGS.REUSE_CLIENT,
        num_workers=EMBEDDING_SETTINGS.NUM_WORKERS,
        additional_kwargs={"encoding_format": "float"}
    )

def _get_embedding_service(
        partition_file_tool_repository: PartitionFileToolRepositoryDep, 
        storage_context: "StorageContextDep", 
        tool_storage_context: "ToolStorageContextDep"
    ) -> EmbeddingService:
    return EmbeddingService(partition_file_tool_repository, storage_context, tool_storage_context)

def _get_vector_store(
        partition: ValidPartitionDep,
        qdrant_client: QdrantDep,
        sync_qdrant_client: QdrantSyncDep,
        embed_model: "EmbedModelDep",
    ) -> QdrantVectorStore:
    return QdrantVectorStore(
        collection_name = str(partition.collection_id),
        enable_hybrid=True,
        embed_model=embed_model,
        fastembed_sparse_model="Qdrant/bm42-all-minilm-l6-v2-attentions",
        batch_size=50,
        aclient=qdrant_client,
        client=sync_qdrant_client,
    )

def _get_tool_vector_store(
        partition: ValidPartitionDep,
        qdrant_client: QdrantDep, 
        sync_qdrant_client: QdrantSyncDep,
        embed_model: "EmbedModelDep",
    ) -> QdrantVectorStore:
    return QdrantVectorStore(
        collection_name = get_tool_partition(partition.id),
        enable_hybrid=True,
        embed_model=embed_model,
        fastembed_sparse_model="Qdrant/bm42-all-minilm-l6-v2-attentions",
        batch_size=50,
        aclient=qdrant_client,
        client=sync_qdrant_client,
    )

def _get_doc_store(partiton: ValidPartitionDep) -> PostgresDocumentStore:
   return PostgresDocumentStore.from_uri(
       uri=str(settings.POSTGRES_SYNC_DSN),
       namespace=str(partiton.id),
       schema_name="llama_index",
       table_name="doc_store"
   )

def _get_index_store(partiton: ValidPartitionDep) -> PostgresIndexStore:
   return PostgresIndexStore.from_uri(
       uri=str(settings.POSTGRES_SYNC_DSN),
       namespace=str(partiton.id),
       schema_name="llama_index",
       table_name="index_store"
   )


def _get_storage_context(
    vector_store: "VectorStoreDep",
    doc_store: "DocStoreDep",
    index_store: "IndexStoreDep",
) -> StorageContext:
    return StorageContext.from_defaults(
        docstore=doc_store, 
        index_store=index_store, 
        vector_store=vector_store
    )

def _get_tool_storage_context(
    vector_store: "ToolVectorStoreDep",
    doc_store: "DocStoreDep",
    index_store: "IndexStoreDep",
) -> StorageContext:
    return StorageContext.from_defaults(
        docstore=doc_store, 
        index_store=index_store, 
        vector_store=vector_store
    )

VectorStoreDep = Annotated[QdrantVectorStore, Depends(_get_vector_store)]
ToolVectorStoreDep = Annotated[QdrantVectorStore, Depends(_get_tool_vector_store)]
DocStoreDep = Annotated[PostgresDocumentStore, Depends(_get_doc_store)]
IndexStoreDep = Annotated[PostgresIndexStore, Depends(_get_index_store)]
EmbedModelDep = Annotated[OpenAILikeEmbedding, Depends(_get_embed_model_v2)]
StorageContextDep = Annotated[StorageContext, Depends(_get_storage_context)]
ToolStorageContextDep = Annotated[StorageContext, Depends(_get_tool_storage_context)]
EmbeddingServiceDep = Annotated[EmbeddingService, Depends(_get_embedding_service)]
