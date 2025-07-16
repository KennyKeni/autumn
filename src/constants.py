from enum import Enum
from typing import TypeVar

from src.model import Base


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    