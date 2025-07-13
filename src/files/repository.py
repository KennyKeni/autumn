from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.files.constants import FileDbStatus
from src.files.models.file import File
from src.files.schemas.requests import FileCreate, FileUpdate
from src.repository import SqlRepository


class FileSqlRepository(SqlRepository[File, FileCreate, FileUpdate]):
    def __init__(self, postgres_session: AsyncSession):
        super().__init__(postgres_session, File, File.status != FileDbStatus.DELETED)

    async def update_status(self, file_id: str, status: FileDbStatus) -> Optional[File]:
        file_data = FileUpdate(status=status)
        result = await self.update_by_id(file_id, file_data)
        return result
