from uuid import UUID
from pydantic import BaseModel, Field

from src.files.constants import FileStatus, MimeType
from src.files.models.file import File


class GetFileResponse(BaseModel):
    id: UUID
    file_name: str
    mime_type: MimeType
    file_size: int
    bucket_name: str
    object_key: str
    status: FileStatus

    @classmethod
    def from_db_model(cls, file_model: File):
        return cls(
            id=file_model.id,
            file_name=file_model.file_name,
            mime_type=file_model.mime_type,
            file_size=file_model.file_size,
            bucket_name=file_model.bucket_name,
            object_key=file_model.object_key,
            status=file_model.status,
        )
