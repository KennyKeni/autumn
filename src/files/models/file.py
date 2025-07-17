from typing import TYPE_CHECKING, List
import uuid

from sqlalchemy import UUID, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.files.constants import FileDbStatus, MimeType
from src.model import TrackedBase

if TYPE_CHECKING:
    from src.partitions.models.partition import Partition
    from src.partitions.models.partition_files import PartitionFile


class File(TrackedBase):
    __tablename__: str = "files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    mime_type: Mapped[MimeType] = mapped_column(String(32), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer(), nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(256), nullable=False)
    object_key: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[FileDbStatus] = mapped_column(
        String(256), nullable=False, default=FileDbStatus.PENDING
    )

    partition_files: Mapped[List["PartitionFile"]] = relationship(
        "PartitionFile",
        back_populates="file",
        cascade="all, delete-orphan"
    )

    partitions: Mapped[List["Partition"]] = relationship(
        "Partition", 
        secondary="partition_files",
        viewonly=True,
        overlaps="partition_files",
    )

    __table_args__ = (
        Index(None, "status"),
        Index(None, "bucket_name"),
        Index(None, "object_key"),
        Index(None, "bucket_name", "status"),
    )
