import uuid
from sqlalchemy import UUID, Integer, String, null
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from files.constants import ContentType, FileStatus


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mime_type: Mapped[ContentType] = mapped_column(String(32), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(256), nullable=False)
    object_key: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[FileStatus] = mapped_column(String(256), nullable=False, default=FileStatus.PENDING)
    
    ### Qdrant ###
    # collection: Mapped[str] = mapped_column(String(256), nullable=True)