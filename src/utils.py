
from typing import Any, Optional, Type, TypeVar
import uuid

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

T = TypeVar('T')
def get_instance_var(instance: Any, key: str, expected_type: Type[T]) -> T:
    var: Any = instance.__dict__[key]
    if isinstance(var, expected_type):
        return var
    raise ValueError(f"Expected value of type {expected_type.__name__}, got {type(var).__name__}")



    


# class Test(BaseObjectNodeMapping[BaseTool]):
#     def __init__(self, objs: Optional[Sequence[BaseTool]] = None) -> None:
#         objs = objs or []
        
#         try:
#             self._tools = {getattr(tool, "id"): tool for tool in objs}
#         except AttributeError as e:
#             raise AttributeError("All tools must have 'id' attribute") from e


