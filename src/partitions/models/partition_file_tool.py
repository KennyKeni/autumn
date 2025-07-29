import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model import TrackedBase
from src.partitions.constants import PartitionFileToolType

if TYPE_CHECKING:
    from src.partitions.models.partition_file import PartitionFile

class PartitionFileTool(TrackedBase):
    __tablename__ = "partition_file_tools"

    # Implicitly refer to the index id AND node id
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    tool_group: Mapped[str] = mapped_column(String(128), nullable=False, default="default")

    tool_type: Mapped[PartitionFileToolType] = mapped_column(String(128), nullable=False)

    partition_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("partition_files.id"), nullable=False
    )

    # Relationships
    partition_file: Mapped["PartitionFile"] = relationship(
        "PartitionFile",
        back_populates="partition_file_tools"
    )

    __table_args__ = (
        Index(None, "partition_file_id"),
    )


