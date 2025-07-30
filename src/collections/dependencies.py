from typing import Annotated

from fastapi import Depends

from src.collections.models.collection import Collection
from src.collections.repository import CollectionSqlRepository
from src.collections.service import CollectionService
from src.dependencies import PostgresDep
from src.factory import validate_entity_exists_factory


def _get_collection_repository(postgres_dep: PostgresDep) -> CollectionSqlRepository:
    return CollectionSqlRepository(postgres_dep)


CollectionRepositoryDep = Annotated[
    CollectionSqlRepository, Depends(_get_collection_repository)
]


def _get_collection_service(
    collection_repository: CollectionRepositoryDep,
) -> CollectionService:
    return CollectionService(collection_repository)


CollectionServiceDep = Annotated[CollectionService, Depends(_get_collection_service)]
ValidCollectionDep = Annotated[
    Collection,
    Depends(
        validate_entity_exists_factory(
            Collection, _get_collection_repository, "collection_id"
        )
    ),
]
