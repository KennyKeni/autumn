from typing import TYPE_CHECKING
import uuid

from sqlalchemy import UUID, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model import TrackedBase

if TYPE_CHECKING:
    from src.partitions.models.partition import Partition
    from src.files.models.file import File

# If this overcomplicates, use 'Table' instead
class PartitionFile(TrackedBase):
    __tablename__ = "partition_files"
    
    partition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partitions.id"), nullable=False
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("files.id"), nullable=False
    )

    partition: Mapped["Partition"] = relationship(
        "Partition",
        back_populates="partition_files"
    )
    
    file: Mapped["File"] = relationship(
        "File", 
        back_populates="partition_files"
    )
    
    __table_args__ = (
        PrimaryKeyConstraint("partition_id", "file_id"),

        Index(None, "partition_id"),
        Index(None, "file_id"),
    )