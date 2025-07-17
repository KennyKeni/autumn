from typing import Annotated, Any, TypeVar, Type, Callable, Awaitable
from uuid import UUID
from fastapi import Depends, Path
from src.dependencies import PostgresDep
from src.exceptions import EntityNotFoundError
from src.model import Base
from src.repository import SqlRepository

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=SqlRepository)

EntityValidator = Callable[[UUID, RepositoryType], Awaitable[ModelType]]

def create_entity_validator(
    entity_class: Type[ModelType],
    repository_dependency: Callable[..., RepositoryType],
    param_name: str,
    *conditions: Any,
    skip_defaults=False,
) -> EntityValidator:
    async def validate_entity_exists(
        entity_id: UUID = Path(..., alias=param_name),
        repository: RepositoryType = Depends(repository_dependency)
    ) -> ModelType:
        entity = await repository._get_by_id(
            id=entity_id, 
            skip_defaults=skip_defaults, 
            *conditions
        )
        if not entity:
            raise EntityNotFoundError(entity_class, str(entity_id))
        return entity
    return validate_entity_exists

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