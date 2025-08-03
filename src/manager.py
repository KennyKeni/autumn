import time
from typing import Dict

from llama_index.vector_stores.qdrant.utils import (
    SparseEncoderCallable,
    fastembed_sparse_encoder,
)

from src.model import CachedFastEmbedModel


class FastEmbedManager:
    def __init__(self, ttl_seconds: int = 1800):  # 30 minutes default
        self.fast_embed_models: Dict[str, CachedFastEmbedModel] = {}
        self.ttl_seconds = ttl_seconds

    def _cleanup_expired(self):
        current_time = time.time()
        expired_keys = [
            key
            for key, cached in self.fast_embed_models.items()
            if current_time - cached.last_accessed > self.ttl_seconds
        ]
        for key in expired_keys:
            del self.fast_embed_models[key]

    def get_fastembed_model(self, fast_embed_model: str) -> SparseEncoderCallable:
        fastembed_sparse_model = None
        cached = self.fast_embed_models.get(fast_embed_model)
        if cached:
            cached.last_accessed = time.time()
            fastembed_sparse_model = cached.model
        else:
            fastembed_sparse_model = fastembed_sparse_encoder(
                model_name=fast_embed_model
            )
            current_time = time.time()
            self.fast_embed_models[fast_embed_model] = CachedFastEmbedModel(
                model=fastembed_sparse_model,
                last_accessed=current_time,
                created_at=current_time,
            )

        self._cleanup_expired()
        return fastembed_sparse_model


fast_embed_manager = FastEmbedManager()
