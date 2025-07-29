import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import UUID, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.model import TrackedBase
from src.partitions.constants import PartitionDbStatus

if TYPE_CHECKING:
    from src.collections.models.collection import Collection
    from src.partitions.models.partition_file import PartitionFile

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

    __table_args__ = (
        Index(None, "collection_id"),
    )
