from typing import Annotated

from fastapi import Depends
from src.dependencies import PostgresDep
from src.files.repository import FileRepository
from src.files.service import FileService


def _get_file_repository(postgres_dep: PostgresDep) -> FileRepository:
    return FileRepository(postgres_dep)


FileRepositoryDep = Annotated[FileRepository, Depends(_get_file_repository)]


def _get_file_service(file_repository: FileRepositoryDep) -> FileService:
    return FileService(file_repository)


FileServiceDep = Annotated[FileService, Depends(_get_file_service)]
