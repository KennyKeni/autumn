import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import UUID, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model import TrackedBase
from src.partitions.constants import PartitionDbStatus

if TYPE_CHECKING:
    from src.partitions.models.partition_files import PartitionFile
    from src.files.models.file import File
    from src.collections.models.collection import Collection

class Partition(TrackedBase):
    __tablename__ = "partitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collections.id"), nullable=False
    )
    status: Mapped[PartitionDbStatus] = mapped_column(String(128), nullable=False, default=PartitionDbStatus.ACTIVE)

    collection: Mapped["Collection"] = relationship(
        "Collection",
        back_populates="partitions"
    )

    partition_files: Mapped[List["PartitionFile"]] = relationship(
        "PartitionFile",
        back_populates="partition",
        cascade="all, delete-orphan"
    )

    files: Mapped[List["File"]] = relationship(
        "File",
        secondary="partition_files",
        viewonly=True,
        overlaps="partition_files"
    )

    __table_args__ = (Index("idx_partitions_collection_id", "collection_id"),)
