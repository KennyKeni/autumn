from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FilesConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="EMBEDDING_",
        extra="ignore",
    )

    FILE_TOLERANCE: int = Field(
        default=1028, description="File size tolerance limit of presigned URL"
    )  # Currently unsupported


filesConfig = FilesConfig()  # type:ignore
