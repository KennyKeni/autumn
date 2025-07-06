from typing import Self
from src.files.models.file import File
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from pydantic import BaseModel, Field, model_validator


class SentenceSplitterRequest(BaseModel):
    pass
    # seperator: str = Field(default=, description="")
    # chunk_size: int = Field(default=, description="")
    # chunk_overlap: int =


class EmbedFileRequest(BaseModel):
    file_id: str = Field(..., description="File id of uploaded file")
    collection_name: str = Field(..., description="Qdrant Collection")


# class SentenceSplitter(
#     separator: str = " ",
#     chunk_size: int = DEFAULT_CHUNK_SIZE,
#     chunk_overlap: int = SENTENCE_CHUNK_OVERLAP,
#     tokenizer: ((...) -> Unknown) | None = None,
#     paragraph_separator: str = DEFAULT_PARAGRAPH_SEP,
#     chunking_tokenizer_fn: ((str) -> List[str]) | None = None,
#     secondary_chunking_regex: str | None = CHUNKING_REGEX,
#     callback_manager: CallbackManager | None = None,
#     include_metadata: bool = True,
#     include_prev_next_rel: bool = True,
#     id_func: ((...) -> Unknown) | None = None
