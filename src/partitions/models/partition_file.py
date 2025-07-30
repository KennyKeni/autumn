import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import UUID, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model import TrackedBase

if TYPE_CHECKING:
    from src.files.models.file import File
    from src.partitions.models.partition import Partition
    from src.partitions.models.partition_file_tool import PartitionFileTool


# First class entity due to complexity
class PartitionFile(TrackedBase):
    __tablename__ = "partition_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    partition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partitions.id"), nullable=False
    )

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id"), nullable=False
    )

    # Relationships
    partition: Mapped["Partition"] = relationship(
        "Partition", back_populates="partition_files"
    )

    file: Mapped["File"] = relationship("File", back_populates="partition_files")

    partition_file_tools: Mapped[List["PartitionFileTool"]] = relationship(
        "PartitionFileTool",
        back_populates="partition_file",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("partition_id", "file_id"),
        Index(None, "partition_id"),
        Index(None, "file_id"),
    )
