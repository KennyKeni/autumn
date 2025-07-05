from pydantic import BaseModel, Field

from src.files.constants import MimeType


class CreatePresignedUrlRequest(BaseModel):
    file_name: str = Field(default="user-uploaded-content", description="Image file name.")
    mime_type: MimeType = Field(..., description="MIME Type.")
    file_size: int = Field(description="File size in bytes", gt=0)