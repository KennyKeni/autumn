from typing import Any, Optional

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.vector_stores.qdrant.utils import (
    HybridFusionCallable,
    SparseEncoderCallable,
)
from qdrant_client import AsyncQdrantClient
from qdrant_client.conversions.common_types import QuantizationConfig
from qdrant_client.http import models as rest


class QdrantVectorStoreAsync(QdrantVectorStore):
    def __init__(
        self,
        collection_name: str,
        aclient: Optional[AsyncQdrantClient] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        batch_size: int = 64,
        parallel: int = 4,
        max_retries: int = 3,
        client_kwargs: Optional[dict[Any, Any]] = None,
        dense_config: Optional[rest.VectorParams] = None,
        sparse_config: Optional[rest.SparseVectorParams] = None,
        quantization_config: Optional[QuantizationConfig] = None,
        enable_hybrid: bool = False,
        fastembed_sparse_model: Optional[str] = None,
        sparse_doc_fn: Optional[SparseEncoderCallable] = None,
        sparse_query_fn: Optional[SparseEncoderCallable] = None,
        hybrid_fusion_fn: Optional[HybridFusionCallable] = None,
        index_doc_id: bool = True,
        text_key: Optional[str] = "text",
        dense_vector_name: Optional[str] = None,
        sparse_vector_name: Optional[str] = None,
    ) -> None:
        super().__init__(  # pyright: ignore[reportUnknownMemberType]
            collection_name=collection_name,
            client=None,
            aclient=aclient,
            url=url,
            api_key=api_key,
            batch_size=batch_size,
            parallel=parallel,
            max_retries=max_retries,
            client_kwargs=client_kwargs,
            dense_config=dense_config,
            sparse_config=sparse_config,
            quantization_config=quantization_config,
            enable_hybrid=enable_hybrid,
            fastembed_sparse_model=fastembed_sparse_model,
            sparse_doc_fn=sparse_doc_fn,
            sparse_query_fn=sparse_query_fn,
            hybrid_fusion_fn=hybrid_fusion_fn,
            index_doc_id=index_doc_id,
            text_key=text_key,
            dense_vector_name=dense_vector_name,
            sparse_vector_name=sparse_vector_name,
        )

    def use_old_sparse_encoder(self, collection_name: str) -> bool:
        return False
