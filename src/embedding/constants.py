# TODO Potentially store these in the database
from enum import Enum


class EmbeddingModel(str, Enum):
    QWEN3_8B = "qwen/qwen3-embedding-8b"

