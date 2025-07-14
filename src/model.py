from datetime import datetime

from sqlalchemy import DateTime, func, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.constants import SQL_ALCHEMY_NAMING_CONVENTION

class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=SQL_ALCHEMY_NAMING_CONVENTION)

class TrackedBase(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
