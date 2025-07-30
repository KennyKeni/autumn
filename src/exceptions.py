from typing import Any, Type, Union

from fastapi import HTTPException, status

from src.model import Base


class EntityNotFoundError(HTTPException):
    def __init__(self, entity: Type[Base], entity_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity.__name__} of ID {entity_id} not found",
        )


class DuplicateEntityError(HTTPException):
    def __init__(self, entity: Type[Base]) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity.__name__} already exists",
        )


class ValidationMatchHTTPException(HTTPException):
    def __init__(self, entity: Union[Type[Base], str]) -> None:
        entity_type = entity if isinstance(entity, str) else entity.__name__
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{entity_type} ID does not match provided ID",
        )


class ValidationHTTPException(HTTPException):
    def __init__(self, entity: Any, expected_type: type) -> None:
        entity_type = entity if isinstance(entity, str) else entity.__name__
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{entity_type} was not of expected type: {expected_type}",
        )

