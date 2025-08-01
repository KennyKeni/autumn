from typing import Any, Awaitable, Callable, Optional, Type
from uuid import UUID

from fastapi import Depends, Path, Query

from src.exceptions import EntityNotFoundError
from src.model import Base
from src.repository import SqlRepository


def validate_entity_exists_factory[
    ModelType: Base,
](
    entity_class: Type[ModelType],
    repository_dependency: Callable[..., SqlRepository[ModelType, Any, Any]],
    param_name: str,
    *conditions: Any,
    skip_defaults: bool = False,
) -> Callable[..., Awaitable[ModelType]]:
    async def validate_entity_exists(
        entity_id: UUID = Path(..., alias=param_name),
        repository: SqlRepository[ModelType, Any, Any] = Depends(repository_dependency),
    ) -> ModelType:

        entity: Optional[ModelType] = await repository.get_by_id(
            id=entity_id,
            *conditions,
            skip_defaults=skip_defaults,
        )
        if entity is None:
            raise EntityNotFoundError(entity_class, str(entity_id))
        return entity

    return validate_entity_exists


def get_id_from_path_factory(id_name: str) -> Callable[[UUID], UUID]:
    def get_id_from_path(
        entity_id: UUID = Path(..., alias=id_name),
    ) -> UUID:
        return entity_id

    return get_id_from_path


def get_id_from_param_factory(id_name: str) -> Callable[[UUID], UUID]:
    def get_id_from_param(
        path_id: UUID = Query(..., alias=id_name),
    ) -> UUID:
        return path_id

    return get_id_from_param


# Doesn't work really work as expected
# def annotated_entity_validator(
#     entity_class: Type[ModelType],
#     repository_dependency: Callable[..., RepositoryType],
#     *conditions: Any,
#     skip_defaults = False,
# ):
#     return Annotated[
#         entity_class,
#         create_entity_validator(
#             entity_class=entity_class,
#             repository_dependency=repository_dependency,
#             skip_defaults=skip_defaults, *conditions
#         )
#     ]
