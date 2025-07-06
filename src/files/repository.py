from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.files.constants import FileStatus
from src.files.models.file import File
from src.files.schemas.requests import FileCreate, FileUpdate


class FileRepository:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def get_all(self, offset: int = 0, limit: int = 50) -> Sequence[File]:
        result = await self.postgres_session.scalars(
            select(File)
            .where(File.status != FileStatus.DELETED)
            .offset(offset)
            .limit(limit)
        )
        return result.all()

    async def get_by_id(self, file_id: str) -> Optional[File]:
        result = await self.postgres_session.execute(
            select(File)
            .where(File.id == file_id)
            .where(File.status != FileStatus.DELETED)
        )
        return result.scalar_one_or_none()

    async def create(self, file_data: FileCreate) -> File:
        file = File(**file_data.model_dump())
        self.postgres_session.add(file)
        return file

    async def update_file(self, file_id: str, file_data: FileUpdate):
        file = await self.get_by_id(file_id)
        if not file:
            return None

        update_data = file_data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(file, field, value)

        return file

    async def update_file_status(self, file_id: str, status: FileStatus) -> bool:
        file_data = FileUpdate(status=status)
        result = await self.update_file(file_id, file_data)
        return result is not None

    async def delete(self, file_id: str) -> bool:
        db_file = await self.get_by_id(file_id)
        if db_file:
            await self.postgres_session.delete(db_file)
            return True
        return False
