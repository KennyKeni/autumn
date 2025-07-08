from typing import Any, Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sqlalchemy import delete, func, select, Select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod

from database import Base

### SQL ALCHEMY REPOSITORY ###
# TODO Support conditions with both and_ and or_

ModelType = TypeVar("ModelType", bound=Base)
CreateModelType = TypeVar("CreateModelType", bound=BaseModel)
UpdateModelType = TypeVar("UpdateModelType", bound=BaseModel)

class SqlRepository(Generic[ModelType, CreateModelType, UpdateModelType], ABC):
    def __init__(self, postgres_session: AsyncSession, model_type: Type[ModelType], id_field: str = 'id'):
        self.postgres_session = postgres_session
        self.model_type = model_type
        self.id_field_name = id_field

    @property
    def _id_field(self):
        if not hasattr(self.model_type, self.id_field_name):
            raise AttributeError(f"{self.model_type.__name__} model missing '{self.id_field_name}' field")
        return getattr(self.model_type, self.id_field_name)
    
    # ========== PUBLIC INTERFACE (STABLE) ==========
    
    async def get_all(self, *conditions: Any, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:
        return await self._get_all(*conditions, offset=offset, limit=limit)
    
    async def get_one(self, *conditions: Any) -> Optional[ModelType]:
        return await self._get_one(*conditions)
    
    async def get_by_id(self, id: str | UUID, *conditions: Any) -> Optional[ModelType]:
        return await self._get_by_id(id=id, *conditions)
    
    async def count(self, *conditions: Any) -> int:
        return await self._count(*conditions)
    
    async def create(self, model_data: CreateModelType) -> ModelType:
        return await self._create(model_data=model_data)
    
    async def update(self, id: str | UUID, model_data: UpdateModelType, *conditions: Any) -> Optional[ModelType]:
        return await self._update(id=id, model_data=model_data, *conditions)
    
    async def delete(self, id: str | UUID, *conditions: Any) -> bool:
        return await self._delete(id, *conditions)
    
    async def exists(self, *conditions: Any) -> bool:
        return await self._exists(*conditions)
    
    async def exists_by_id(self, id: str | UUID, *conditions: Any) -> bool:
        return await self._exists(self._id_field == id, *conditions)
    
    ### OPTIONAL BULK OPERATIONS (OVERRIDE IF NEEDED) ###
    
    async def update_all(self, *conditions: Any, model_data: UpdateModelType) -> int:
        raise NotImplementedError(f"{self.__class__.__name__} does not support bulk updates")
    
    async def delete_all(self, *conditions: Any) -> int:
        raise NotImplementedError(f"{self.__class__.__name__} does not support bulk deletes")
    
    ### CUSTOMIZABLE IMPLEMENTATIONS (OVERRIDE TO CUSTOMIZE) ###
    
    async def _get_all(self, *conditions: Any, offset: int = 0, limit: int = 100) -> Sequence[ModelType]:

        query = self._query_builder(*conditions).offset(offset).limit(limit)
        result = await self.postgres_session.scalars(query)
        return result.all()

    async def _get_one(self, *conditions: Any) -> Optional[ModelType]:
        query = self._query_builder(*conditions)
        result = await self.postgres_session.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_by_id(self, id: str | UUID, *conditions: Any) -> Optional[ModelType]:
        return await self._get_one(self._id_field == id, *conditions)

    async def _count(self, *conditions: Any) -> int:
        query = select(func.count()).select_from(self.model_type)
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.postgres_session.execute(query)
        return result.scalar() or 0
    
    async def _create(self, model_data: CreateModelType) -> ModelType:
        instance = self.model_type(**model_data.model_dump())
        self.postgres_session.add(instance)
        return instance
    
    async def _update(self, id: str | UUID, model_data: UpdateModelType, *conditions: Any) -> Optional[ModelType]:
        record = await self._get_by_id(id, *conditions)
        if not record:
            return None
        
        update_dict = model_data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_dict.items():
            if hasattr(record, field):
                setattr(record, field, value)
        
        return record

    async def _delete(self, id: str | UUID, *conditions: Any) -> bool:
        """Override to customize record deletion"""
        record = await self._get_by_id(id, *conditions)
        if record:
            await self.postgres_session.delete(record)
            return True
        return False
    
    async def _exists(self, *conditions: Any) -> bool:
        count = await self._count(*conditions)
        return count > 0
    
    def _query_builder(self, *conditions: Any, query: Optional[Select[Any]] = None) -> Select[Any]:
        if query is None:
            query = select(self.model_type)
        if conditions:
            query = query.where(and_(*conditions))
        return query

### QDRANT REPOSITORY ###

class QdrantRepository(ABC):
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client