from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import settings

# TODO A lot of this will be a dynamic logic in the future.


class EmbeddingConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="EMBEDDING_",
        extra="ignore",
    )

    MODEL_NAME: str = Field(default="Qwen/Qwen3-Embedding-8B", description="")
    API_BASE: str = Field(default="https://api.deepinfra.com/v1/openai", description="")
    API_KEY: str = Field(default=settings.DEEPINFRA_API_KEY, description="")
    API_VERSION: str = Field(default=settings.APP_VERSION)
    EMBED_BATCH_SIZE: int = Field(default=100, description="")
    DIMENSION: Optional[int] = Field(default=4096, description="")
    MAX_RETIRES: int = Field(default=5, description="")
    TIMEOUT: float = Field(default=60.0, description="")
    REUSE_CLIENT: bool = Field(default=True, description="")


embeddingSettings = EmbeddingConfig()  # type: ignore
