from typing import List, Optional, cast
from pydantic import Field, PostgresDsn, RedisDsn, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )
    
    # Database settings
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(description="PostgreSQL database name")
    POSTGRES_USER: str = Field(description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(description="PostgreSQL password")

    POSTGRES_POOL_SIZE: int = Field(default=10, description="SQLAlchemy AsyncEngine Pool Size")
    POSTGRES_MAX_OVERFLOW: int = Field(default=20, description="SQLAlchemy AsyncEngine Overflow Pool Size")
    
    # Qdrant settings
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant host")
    QDRANT_HTTP_PORT: int = Field(default=6333, description="Qdrant REST port")
    QDRANT_GRPC_PORT: int = Field(default=6334, description="Qdrant gRPC port")
    QDRANT_API_KEY: str = Field(description="Qdrant API key")
    QDRANT_TIMEOUT: int = Field(default=60, description="Qdrant Timeout")
    
    # Redis settings
    REDIS_HOST: str = Field(default="localhost", description="Redis Host")
    REDIS_PORT: int = Field(default=6379, description="Redis Port")
    REDIS_PASSWORD: str = Field(description="Redis Password")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, description="Redis Max Connections")

    # S3 Bucket
    S3_ENDPOINT_URL: str = Field(description="S3 Endpoint URL")
    S3_ACCESS_KEY_ID: str = Field(description="S3 Access Key Id")
    S3_SECRET_ACCESS_KEY: str = Field(description="S3 Secret Access Key")
    S3_BUCKET: str = Field(description="S3 Bucket Name")
    
    # API Keys
    OPENROUTER_API_KEY: str = Field(description="OpenRouter API key")
    NOVITA_API_KEY: str = Field(description="Novita API key")

    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    APP_VERSION: str = "1.0"
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, description="Production Environment")

    @computed_field
    @property
    def POSTGRES_DSN(self) -> PostgresDsn:
        """Builds the full PostgreSQL DSN from its components."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,     # Now definitely str
            password=self.POSTGRES_PASSWORD, # Now definitely str
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB            # Now definitely str
        )

    @computed_field
    @property
    def REDIS_DSN(self) -> RedisDsn:
        """Builds the Redis connection DSN from its components."""
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,    # Now definitely str
        )

# Type ignore because I cba dealing with this pydnatic bullshit
settings = Config()  # type: ignore