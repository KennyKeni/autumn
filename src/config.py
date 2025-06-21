from typing import List, Optional
from pydantic import Field, PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
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
    
    # API Keys
    OPENROUTER_API_KEY: str = Field(default="KEY_HERE", description="OpenRouter API key")
    NOVITA_API_KEY: str = Field(default="KEY_HERE", description="Novita API key")

    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    # CORS_ORIGINS_REGEX: str | None = None

    APP_VERSION: str = "1.0"
    ENVIRONMENT: Optional[Environment] = Field(default=Environment.DEVELOPMENT, description="Production Environment")

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
    
    def print_status(self) -> None:
        """Print configuration status"""
        missing = self.check_missing_values()
        if missing:
            print(f"Missing configuration values: {missing}")
        else:
            print("All configuration values are present!")

settings = Config()

print(f"All Settings Present: {settings.validate_all_present()}")  # True/False
print(f"Missing values: {settings.check_missing_values()}")   # ['POSTGRES_DB', 'REDIS_PASSWORD', ...]
settings.print_status()