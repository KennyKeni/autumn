from enum import Enum
from typing import Dict

class ContentType(str, Enum):
    """Supported content types for RAG"""
    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

class FileExtension(str, Enum):
    """Supported file extensions"""
    TXT = ".txt"
    MD = ".md"
    PDF = ".pdf"
    DOCX = ".docx"

class FileStatus(str, Enum):
    """Lifecycle status"""
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"

# Extension to content type mapping
EXTENSION_TO_CONTENT_TYPE: Dict[str, str] = {
    FileExtension.TXT: ContentType.TEXT_PLAIN,
    FileExtension.MD: ContentType.TEXT_MARKDOWN,
    FileExtension.PDF: ContentType.PDF,
    FileExtension.DOCX: ContentType.DOCX,
}

# Reverse mapping
CONTENT_TYPE_TO_EXTENSION: Dict[str, str] = {
    content_type: extension 
    for extension, content_type in EXTENSION_TO_CONTENT_TYPE.items()
}

def is_supported_file(filename: str) -> bool:
    """Check if file type is supported"""
    if not filename or '.' not in filename:
        return False
    
    extension = '.' + filename.split('.')[-1].lower()
    return extension in EXTENSION_TO_CONTENT_TYPE