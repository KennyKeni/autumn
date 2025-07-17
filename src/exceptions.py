from typing import Type

from fastapi import HTTPException, status

from src.model import Base


class EntityNotFoundError(HTTPException):
    def __init__(self, entity: Type[Base], entity_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity.__name__} of ID {entity_id} not found",
        )

class DuplicateEntityError(HTTPException):
    def __init__(self, entity: Type[Base]):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity.__name__} already exists",
        )
