from typing import List, Optional, cast
from pydantic import Field, PostgresDsn, RedisDsn, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Database settings
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: Optional[str] = Field(default=None, description="PostgreSQL database name")
    POSTGRES_USER: Optional[str] = Field(default=None, description="PostgreSQL username")
    POSTGRES_PASSWORD: Optional[str] = Field(default=None, description="PostgreSQL password")

    POSTGRES_POOL_SIZE: int = Field(default=10, description="SQLAlchemy AsyncEngine Pool Size")
    POSTGRES_MAX_OVERFLOW: int = Field(default=20, description="SQLAlchemy AsyncEngine Overflow Pool Size")
    
    # Qdrant settings
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant host")
    QDRANT_HTTP_PORT: int = Field(default=6333, description="Qdrant REST port")
    QDRANT_GRPC_PORT: int = Field(default=6334, description="Qdrant gRPC port")
    QDRANT_API_KEY: Optional[str] = Field(default=None, description="Qdrant API key")
    QDRANT_TIMEOUT: int = Field(default=60, description="Qdrant Timeout")
    
    # Redis settings
    REDIS_HOST: str = Field(default="localhost", description="Redis Host")
    REDIS_PORT: int = Field(default=6379, description="Redis Port")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis Password")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, description="Redis Max Connections")

    # S3 Bucket
    S3_ENDPOINT_URL: Optional[str] = Field(default=None, description="S3 Endpoint URL")
    S3_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="S3 Access Key Id")
    S3_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="S3 Secret Access Key")
    S3_BUCKET: Optional[str] = Field(default=None, description="S3 Bucket Name")
    
    # API Keys
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, description="OpenRouter API key")
    NOVITA_API_KEY: Optional[str] = Field(default=None, description="Novita API key")

    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    # CORS_ORIGINS_REGEX: str | None = None

    APP_VERSION: str = "1.0"
    ENVIRONMENT: Optional[Environment] = Field(default=Environment.DEVELOPMENT, description="Production Environment")

    @model_validator(mode='after')
    def validate_and_cast_required_fields(self) -> 'Config':
        """Validate required fields and cast them to non-Optional"""
        # Check for missing values
        missing = self.check_missing_values()
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")
        
        # Cast Optional fields to non-Optional after validation, for better type safety
        self.POSTGRES_DB = cast(str, self.POSTGRES_DB)
        self.POSTGRES_USER = cast(str, self.POSTGRES_USER)
        self.POSTGRES_PASSWORD = cast(str, self.POSTGRES_PASSWORD)
        self.REDIS_PASSWORD = cast(str, self.REDIS_PASSWORD)
        self.QDRANT_API_KEY = cast(str, self.QDRANT_API_KEY)
        self.OPENROUTER_API_KEY = cast(str, self.OPENROUTER_API_KEY)
        self.NOVITA_API_KEY = cast(str, self.NOVITA_API_KEY)
        self.S3_ENDPOINT_URL = cast(str, self.S3_ENDPOINT_URL)
        self.S3_ACCESS_KEY_ID = cast(str, self.S3_ACCESS_KEY_ID)
        self.S3_SECRET_ACCESS_KEY = cast(str, self.S3_SECRET_ACCESS_KEY)
        self.S3_BUCKET = cast(str, self.S3_BUCKET)
        
        return self

    @computed_field
    @property
    def POSTGRES_DSN(self) -> PostgresDsn:
        """
        Asynchronously builds the full PostgreSQL DSN from its components.
        """
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )


    @computed_field
    @property
    def REDIS_DSN(self) -> RedisDsn:
        """
        Builds the Redis connection DSN from its components.
        """
        # The path corresponds to the database number in a Redis URI
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
        )

    def check_missing_values(self) -> List[str]:
        """Return list of missing (None) configuration values"""
        missing = []
        for field_name, field_value in self.model_dump().items():
            if field_value is None:
                missing.append(field_name)
        return missing
    
    def validate_all_present(self) -> bool:
        """Check if all configuration values are present"""
        return len(self.check_missing_values()) == 0

settings = Config()