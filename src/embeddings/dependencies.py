from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from llama_index.embeddings.openai_like import OpenAILikeEmbedding

from embeddings.config import embeddingSettings as settings

# TODO Add dynamic model selection in the future

@lru_cache()
def _get_emebed_model() -> OpenAILikeEmbedding:
    return OpenAILikeEmbedding(
        model_name=settings.MODEL_NAME,
        api_base=settings.API_BASE,
        api_key=settings.API_KEY,
        api_version=settings.API_VERSION,
        embed_batch_size=settings.EMBED_BATCH_SIZE,
        max_retries=settings.MAX_RETIRES,
        timeout=settings.TIMEOUT,
        dimensions=settings.DIMENSION,
        reuse_client=settings.REUSE_CLIENT,
    )

EmbedModel = Annotated[OpenAILikeEmbedding, Depends(_get_emebed_model)]