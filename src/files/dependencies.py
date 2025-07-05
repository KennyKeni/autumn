from typing import Annotated

from fastapi import Depends
from src.files.service import FileService


def _get_file_service() -> FileService:
    return FileService()

FileServiceDep = Annotated[FileService, Depends(_get_file_service)]