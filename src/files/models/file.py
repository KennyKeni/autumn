import uuid

from sqlalchemy import UUID, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.files.constants import FileDbStatus, MimeType
from src.model import TrackedBase


class File(TrackedBase):
    __tablename__: str = "files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    mime_type: Mapped[MimeType] = mapped_column(String(32), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer(), nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(256), nullable=False)
    object_key: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[FileDbStatus] = mapped_column(
        String(256), nullable=False, default=FileDbStatus.PENDING
    )

    __table_args__ = (
        Index("idx_files_status", "status"),
        Index("idx_files_bucket_name", "bucket_name"),
        Index("idx_files_object_key", "object_key"),
        Index("idx_files_bucket_status", "bucket_name", "status"),
    )
