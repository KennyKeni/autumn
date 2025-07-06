from enum import Enum
from typing import Dict

class MimeType(str, Enum):
    """Supported content types for RAG"""
    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    JPEG = "image/jpeg"

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
    DELETED = "deleted"

# Extension to content type mapping
EXTENSION_TO_CONTENT_TYPE: Dict[str, str] = {
    FileExtension.TXT: MimeType.TEXT_PLAIN,
    FileExtension.MD: MimeType.TEXT_MARKDOWN,
    FileExtension.PDF: MimeType.PDF,
    FileExtension.DOCX: MimeType.DOCX,
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