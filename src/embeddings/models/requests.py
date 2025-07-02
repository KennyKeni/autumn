from typing import Optional, Self
from fastapi import UploadFile
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from pydantic import BaseModel, Field, model_validator

class SentenceSplitterRequest(BaseModel):
    pass
    # seperator: str = Field(default=, description="")
    # chunk_size: int = Field(default=, description="")
    # chunk_overlap: int = 

class EmbedFileRequest(BaseModel):
    file: UploadFile = Field(description="Uploaded file")
    collection_name: str = Field(default="", description="Qdrant Collection")

    @model_validator(mode='after')
    def validate_and_set_defaults(self) -> Self:
        if not hasattr(self.file, 'filename') or not self.file.filename:
            raise ValueError("File must have a filename")
        
        if not hasattr(self.file, 'content_type') or not self.file.content_type:
            raise ValueError("File must have a content_type")
        
        if not self.collection:
            self.collection = self.file.filename

        return self




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