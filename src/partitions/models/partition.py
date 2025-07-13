import uuid
from typing import Optional

from sqlalchemy import UUID, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.model import TrackedBase
from src.partitions.constants import PartitionDbStatus


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

    __table_args__ = (Index("idx_partitions_collection_id", "collection_id"),)
