from typing import Optional

from pydantic import BaseModel

from src.files.constants import FileDbStatus, MimeType


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
