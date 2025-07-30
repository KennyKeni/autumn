# TODO Potentially store these in the database
from enum import Enum


class EmbeddingModel(str, Enum):
    QWEN3_8B = "Qwen/Qwen3-Embedding-8B"
