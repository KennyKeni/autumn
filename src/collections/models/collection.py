import uuid
from typing import TYPE_CHECKING, List, Optional

from qdrant_client.models import Distance
from sqlalchemy import UUID, Boolean, Integer, String, null
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.collections.config import collectionSettings
from src.collections.constants import CollectionDbStatus
from src.embedding.constants import EmbeddingModel
from src.model import TrackedBase

if TYPE_CHECKING:
    from src.partitions.models.partition import Partition


class Collection(TrackedBase):
    __tablename__: str = "collections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(), nullable=False,
    )
    embedding_model: Mapped[EmbeddingModel] = mapped_column(
        String(), nullable=False, default=collectionSettings.EMBEDDING_MODEL
    )
    vector_dimension: Mapped[int] = mapped_column(
        Integer(), nullable=False, default=collectionSettings.VECTOR_DIMENSION
    )
    vector_distance: Mapped[Distance] = mapped_column(
        String(128),
        nullable=False,
        default=collectionSettings.VECTOR_DISTANCE,
    )
    vector_on_disk: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, default=collectionSettings.VECTOR_ON_DISK
    )
    shard_number: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=collectionSettings.SHARD_NUMBER,
    )
    replication_factor: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=collectionSettings.REPLICATION_FACTOR,
    )
    hnsw_m: Mapped[Optional[int]] = mapped_column(
        Integer(), nullable=False, default=collectionSettings.HNSW_M
    )
    hnsw_payload_m: Mapped[Optional[int]] = mapped_column(
        Integer(), nullable=False, default=collectionSettings.HNSW_PAYLOAD_M
    )
    hnsw_on_disk: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    status: Mapped[CollectionDbStatus] = mapped_column(
        String(64), nullable=False, default=collectionSettings.STATUS
    )

    partitions: Mapped[List["Partition"]] = relationship(
        "Partition",
        back_populates="collection",
        cascade="all, delete-orphan"
    )

    # TODO Add more parameters in the future as needed
    # TODO Seperate out certain configs to their own individual model
