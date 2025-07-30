from abc import ABC
from typing import Any, Optional, Sequence, Tuple, Type, Union
from uuid import UUID

from pydantic import BaseModel
from qdrant_client import QdrantClient
from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model import Base


class SqlRepository[
    ModelType: Base, CreateModelType: BaseModel, UpdateModelType: BaseModel
](ABC):
    def __init__(
        self,
        session: AsyncSession,
        model_type: Type[ModelType],
        *default_conditions: Any,
        id_field: str = "id",
    ):
        self.session = session
        self.model_type = model_type
        self.id_field_name = id_field
        self.default_conditions: Tuple[Any, ...] = default_conditions

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
        skip_defaults: bool = False,
    ) -> Sequence[ModelType]:
        return await self._get_all(
            *conditions,
            offset=offset,
            limit=limit,
            skip_defaults=skip_defaults,
        )

    async def get_one(
        self, *conditions: Any, skip_defaults: bool = False
    ) -> Optional[ModelType]:
        return await self._get_one(*conditions, skip_defaults=skip_defaults)

    async def get_by_id(
        self, id: str | UUID, *conditions: Any, skip_defaults: bool = False
    ) -> Optional[ModelType]:
        return await self._get_by_id(id, *conditions, skip_defaults=skip_defaults)

    async def count(self, *conditions: Any, skip_defaults: bool = False) -> int:
        return await self._count(*conditions, skip_defaults=skip_defaults)

    async def create(self, model_data: CreateModelType) -> ModelType:
        return await self._create(model_data=model_data)

    async def update_by_id(
        self,
        id: str | UUID,
        model_data: UpdateModelType,
        *conditions: Any,
        skip_defaults: bool = False,
    ) -> Optional[ModelType]:
        return await self._update_by_id(
            id,
            model_data,
            *conditions,
            skip_defaults=skip_defaults,
        )

    async def delete_by_id(
        self, id: str | UUID, *conditions: Any, skip_defaults: bool = False
    ) -> Optional[ModelType]:
        return await self._delete_by_id(id, *conditions, skip_defaults=skip_defaults)

    async def exists(self, *conditions: Any, skip_defaults: bool = False) -> bool:
        return await self._exists(*conditions, skip_defaults=skip_defaults)

    async def exists_by_id(
        self, id: str | UUID, *conditions: Any, skip_defaults: bool = False
    ) -> bool:
        return await self._exists_by_id(id, *conditions, skip_defaults=skip_defaults)

    async def _get_all(
        self,
        *conditions: Any,
        offset: int = 0,
        limit: int = 100,
        skip_defaults: bool = False,
    ) -> Sequence[ModelType]:
        query = (
            self._query_builder(*conditions, skip_defaults=skip_defaults)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.scalars(query)
        return result.all()

    async def _get_one(
        self, *conditions: Any, skip_defaults: bool = False
    ) -> Optional[ModelType]:
        query = self._query_builder(*conditions, skip_defaults=skip_defaults)
        result = await self.session.execute(query)
        scalar: Optional[ModelType] = result.scalar_one_or_none()
        return scalar

    async def _get_by_id(
        self, id: str | UUID, *conditions: Any, skip_defaults: bool = False
    ) -> Optional[ModelType]:
        return await self._get_one(
            self._id_field == id,
            *conditions,
            skip_defaults=skip_defaults,
        )

    async def _count(self, *conditions: Any, skip_defaults: bool = False) -> int:
        query = select(func.count()).select_from(self.model_type)
        if skip_defaults:
            all_conditions = conditions
        else:
            all_conditions = (*self.default_conditions, *conditions)
        if all_conditions:
            query = query.where(and_(*all_conditions))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def _create(self, model_data: CreateModelType) -> ModelType:
        instance = self.model_type(**model_data.model_dump())
        self.session.add(instance)
        return instance

    async def _update_by_id(
        self,
        id: str | UUID,
        model_data: UpdateModelType,
        *conditions: Any,
        skip_defaults: bool = False,
    ) -> Optional[ModelType]:
        record = await self._get_by_id(id, *conditions, skip_defaults=skip_defaults)
        if not record:
            return None

        update_dict = model_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(record, field):
                setattr(record, field, value)

        return record

    async def _delete_by_id(
        self, id: str | UUID, *conditions: Any, skip_defaults: bool = False
    ) -> Optional[ModelType]:
        record = await self._get_by_id(id, *conditions, skip_defaults=skip_defaults)
        if record:
            await self.session.delete(record)
            return record
        return None

    async def _exists(self, *conditions: Any, skip_defaults: bool = False) -> bool:
        count = await self._count(*conditions, skip_defaults=skip_defaults)
        return count > 0

    async def _exists_by_id(
        self, id: Union[str, UUID], *conditions: Any, skip_defaults: bool = False
    ) -> bool:
        return await self._exists(
            self._id_field == id,
            *conditions,
            skip_defaults=skip_defaults,
        )

    def _query_builder(
        self,
        *conditions: Any,
        query: Optional[Select[Any]] = None,
        skip_defaults: bool = False,
    ) -> Select[Any]:
        if query is None:
            query = select(self.model_type)

        if skip_defaults:
            all_conditions = conditions
        else:
            all_conditions = (*self.default_conditions, *conditions)

        if all_conditions:
            query = query.where(and_(*all_conditions))
        return query


class QdrantRepository(ABC):
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client


# RepositoryType = TypeVar("RepositoryType", bound=SqlRepository[ModelType])
