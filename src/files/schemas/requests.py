from typing import Optional

from pydantic import BaseModel, Field

from src.files.constants import FileDbStatus, MimeType


class CreatePresignedUrlRequest(BaseModel):
    file_name: str = Field(..., description="File name.")
    mime_type: MimeType = Field(..., description="MIME Type.")
    file_size: int = Field(description="File size in bytes", gt=0)


class FileCreate(BaseModel):
    file_name: str
    mime_type: MimeType
    file_size: int
    bucket_name: str
    object_key: str
    status: FileDbStatus = FileDbStatus.PENDING


class FileUpdate(BaseModel):
    file_name: Optional[str] = None
    bucket_name: Optional[str] = None
    object_key: Optional[str] = None
    status: Optional[FileDbStatus] = None
