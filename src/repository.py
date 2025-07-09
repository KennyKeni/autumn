from typing import Any, Generic, Optional, Sequence, Tuple, Type, TypeVar
from uuid import UUID
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sqlalchemy import func, select, Select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC

from src.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateModelType = TypeVar("CreateModelType", bound=BaseModel)
UpdateModelType = TypeVar("UpdateModelType", bound=BaseModel)


class SqlRepository(Generic[ModelType, CreateModelType, UpdateModelType], ABC):
    def __init__(
        self,
        postgres_session: AsyncSession,
        model_type: Type[ModelType],
        *universal_conditions: Any,
        id_field: str = "id",
    ):
        self.postgres_session = postgres_session
        self.model_type = model_type
        self.id_field_name = id_field
        self.universal_conditions: Tuple[Any, ...] = universal_conditions

    @property
    def _id_field(self):
        if not hasattr(self.model_type, self.id_field_name):
            raise AttributeError(
                f"{self.model_type.__name__} model missing '{self.id_field_name}' field"
            )
        return getattr(self.model_type, self.id_field_name)

    async def get_all(
        self,
        *conditions: Any,
        offset: int = 0,
        limit: int = 100,
        ignore_universal_conditions: bool = False,
    ) -> Sequence[ModelType]:
        return await self._get_all(
            *conditions,
            offset=offset,
            limit=limit,
            ignore_universal_conditions=ignore_universal_conditions,
        )

    async def get_one(
        self, *conditions: Any, ignore_universal_conditions: bool = False
    ) -> Optional[ModelType]:
        return await self._get_one(
            *conditions, ignore_universal_conditions=ignore_universal_conditions
        )

    async def get_by_id(
        self, id: str | UUID, ignore_universal_conditions: bool = False
    ) -> Optional[ModelType]:
        return await self._get_by_id(
            id=id, ignore_universal_conditions=ignore_universal_conditions
        )

    async def count(
        self, *conditions: Any, ignore_universal_conditions: bool = False
    ) -> int:
        return await self._count(
            *conditions, ignore_universal_conditions=ignore_universal_conditions
        )

    async def create(self, model_data: CreateModelType) -> ModelType:
        return await self._create(model_data=model_data)

    async def update(
        self,
        id: str | UUID,
        model_data: UpdateModelType,
        ignore_universal_conditions: bool = False,
    ) -> Optional[ModelType]:
        return await self._update(
            id=id,
            model_data=model_data,
            ignore_universal_conditions=ignore_universal_conditions,
        )

    async def delete(
        self, id: str | UUID, ignore_universal_conditions: bool = False
    ) -> bool:
        return await self._delete(
            id, ignore_universal_conditions=ignore_universal_conditions
        )

    async def exists(
        self, *conditions: Any, ignore_universal_conditions: bool = False
    ) -> bool:
        return await self._exists(
            *conditions, ignore_universal_conditions=ignore_universal_conditions
        )

    async def exists_by_id(
        self, id: str | UUID, ignore_universal_conditions: bool = False
    ) -> bool:
        return await self._exists_by_id(
            id, ignore_universal_conditions=ignore_universal_conditions
        )

    async def update_all(
        self,
        *conditions: Any,
        model_data: UpdateModelType,
        ignore_universal_conditions: bool = False,
    ) -> int:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support bulk updates"
        )

    async def delete_all(
        self, *conditions: Any, ignore_universal_conditions: bool = False
    ) -> int:
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support bulk deletes"
        )

    async def _get_all(
        self,
        *conditions: Any,
        offset: int = 0,
        limit: int = 100,
        ignore_universal_conditions: bool = False,
    ) -> Sequence[ModelType]:
        query = (
            self._query_builder(
                *conditions, ignore_universal_conditions=ignore_universal_conditions
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self.postgres_session.scalars(query)
        return result.all()

    async def _get_one(
        self, *conditions: Any, ignore_universal_conditions: bool = False
    ) -> Optional[ModelType]:
        query = self._query_builder(
            *conditions, ignore_universal_conditions=ignore_universal_conditions
        )
        result = await self.postgres_session.execute(query)
        return result.scalar_one_or_none()

    async def _get_by_id(
        self, id: str | UUID, ignore_universal_conditions: bool = False
    ) -> Optional[ModelType]:
        return await self._get_one(
            self._id_field == id,
            ignore_universal_conditions=ignore_universal_conditions,
        )

    async def _count(
        self, *conditions: Any, ignore_universal_conditions: bool = False
    ) -> int:
        query = select(func.count()).select_from(self.model_type)
        if ignore_universal_conditions:
            all_conditions = conditions
        else:
            all_conditions = (*self.universal_conditions, *conditions)
        if all_conditions:
            query = query.where(and_(*all_conditions))
        result = await self.postgres_session.execute(query)
        return result.scalar() or 0

    async def _create(self, model_data: CreateModelType) -> ModelType:
        instance = self.model_type(**model_data.model_dump())
        self.postgres_session.add(instance)
        return instance

    async def _update(
        self,
        id: str | UUID,
        model_data: UpdateModelType,
        ignore_universal_conditions: bool = False,
    ) -> Optional[ModelType]:
        record = await self._get_by_id(
            id, ignore_universal_conditions=ignore_universal_conditions
        )
        if not record:
            return None

        update_dict = model_data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_dict.items():
            if hasattr(record, field):
                setattr(record, field, value)

        return record

    async def _delete(
        self, id: str | UUID, ignore_universal_conditions: bool = False
    ) -> bool:
        record = await self._get_by_id(
            id, ignore_universal_conditions=ignore_universal_conditions
        )
        if record:
            await self.postgres_session.delete(record)
            return True
        return False

    async def _exists(
        self, *conditions: Any, ignore_universal_conditions: bool = False
    ) -> bool:
        count = await self._count(
            *conditions, ignore_universal_conditions=ignore_universal_conditions
        )
        return count > 0

    async def _exists_by_id(
        self, id: str | UUID, ignore_universal_conditions: bool = False
    ) -> bool:
        return await self._exists(
            self._id_field == id,
            ignore_universal_conditions=ignore_universal_conditions,
        )

    def _query_builder(
        self,
        *conditions: Any,
        query: Optional[Select[Any]] = None,
        ignore_universal_conditions: bool = False,
    ) -> Select[Any]:
        if query is None:
            query = select(self.model_type)

        if ignore_universal_conditions:
            all_conditions = conditions
        else:
            all_conditions = (*self.universal_conditions, *conditions)

        if all_conditions:
            query = query.where(and_(*all_conditions))
        return query


class QdrantRepository(ABC):
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client
