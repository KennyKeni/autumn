from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config import SETTINGS
from src.partitions.constants import PartitionFileToolType

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
    API_KEY: str = Field(default=SETTINGS.DEEPINFRA_API_KEY, description="")
    API_VERSION: str = Field(default=SETTINGS.APP_VERSION)
    EMBED_BATCH_SIZE: int = Field(default=100, description="")
    DIMENSION: Optional[int] = Field(default=4096, description="")
    MAX_RETIRES: int = Field(default=5, description="")
    TIMEOUT: float = Field(default=60.0, description="")
    REUSE_CLIENT: bool = Field(default=True, description="")
    NUM_WORKERS: int = Field(default=6)
    DEFAULT_FILE_TOOLS: List[PartitionFileToolType] = Field(
        default=[PartitionFileToolType.SUMMARY, PartitionFileToolType.VECTOR],
        description="Default tools to be embedded",
    )
    DEFAULT_FILE_TOOL_GROUP: str = Field(default="DEFAULT")


EMBEDDING_SETTINGS = EmbeddingConfig()
