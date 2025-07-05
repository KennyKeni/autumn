import uuid
from sqlalchemy import UUID, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from src.files.constants import MimeType, FileStatus


class File(Base):
    __tablename__: str = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str] = mapped_column(String(256), nullable=False)
    mime_type: Mapped[MimeType] = mapped_column(String(32), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(256), nullable=False)
    object_key: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[FileStatus] = mapped_column(String(256), nullable=False, default=FileStatus.PENDING)
