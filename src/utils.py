import uuid
from typing import Any, Optional, Protocol, Type, TypeVar

from pydantic import BaseModel

from src.exceptions import ValidationHTTPException


# TODO Potentially incorporate in replacement of dict access
class IDMixin:
    def set_id(self, id: uuid.UUID) -> None:
        self._id: Optional[str] = str(id)

    @property
    def id(self) -> str:
        if self._id is None:
            raise Exception("Id is not set for BaseTool")
        return self._id


def set_instance_var(instance: Any, key: str, value: Any) -> None:
    instance.__dict__[key] = value


T = TypeVar("T")


def get_instance_var(instance: Any, key: str, expected_type: Type[T]) -> T:
    try:
        var: Any = instance.__dict__[key]
    except KeyError:
        raise AttributeError(f"Instance variable '{key}' not found in __dict__")

    if isinstance(var, expected_type):
        return var
    raise ValueError(
        f"Expected value of type {expected_type.__name__}, got {type(var).__name__}"
    )


def assert_isinstance(value: Any, expected_type: Type[T]) -> T:
    if isinstance(value, expected_type):
        return value
    raise ValidationHTTPException(value, expected_type)


class EntityLike(Protocol):
    id: uuid.UUID


class RepositoryBaseModel(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True,
    }
