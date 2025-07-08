from typing import Optional
import uuid
from sqlalchemy import UUID, Boolean, CheckConstraint, Index, Integer, String, null
from sqlalchemy.orm import Mapped, mapped_column
from qdrant_client.models import Distance
from src.database import Base


class Collection(Base):
    __tablename__: str = "collections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vector_dimension: Mapped[int] = mapped_column(Integer(), nullable=False)
    vector_distance: Mapped[Distance] = mapped_column(
        String(128), nullable=False, default=Distance.COSINE
    )
    vector_on_disk: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, default=False
    )
    hnsw_m: Mapped[Optional[int]] = mapped_column(
        Integer(), nullable=True, default=None
    )
    hnsw_payload_m: Mapped[Optional[int]] = mapped_column(
        Integer(), nullable=True, default=None
    )
    hnsw_on_disk: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    # TODO Add more parameters in the future as needed
    # TODO Seperate out certain configs to their own individual model
