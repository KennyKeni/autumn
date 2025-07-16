from datetime import datetime
from typing import TypeVar
from pydantic import BaseModel

from sqlalchemy import DateTime, func, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

SQL_ALCHEMY_NAMING_CONVENTION = {
    # Indexes: idx_tablename_columnname(s)
    "ix": "idx_%(table_name)s_%(column_0_label)s",
    
    # Unique constraints: uq_tablename_columnname(s) 
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    
    # Check constraints: ck_tablename_constraintname
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    
    # Foreign keys: fk_tablename_columnname
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    
    # Primary keys: pk_tablename
    "pk": "pk_%(table_name)s",
}

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

ModelType = TypeVar("ModelType", bound=Base)
CreateModelType = TypeVar("CreateModelType", bound=BaseModel)
UpdateModelType = TypeVar("UpdateModelType", bound=BaseModel)