from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from src.files.constants import FileStatus
from src.files.repository import FileRepository
from src.files.schemas.requests import CreatePresignedUrlRequest, FileCreate
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.files.models.file import File
from src.files.schemas.responses import GetFileResponse


class FileService:
    def __init__(self, file_repository: FileRepository):
        self.file_repository = file_repository

    async def get_all(
        self,
        offset: int,
        limit: int,
    ):
        """Get all files, within limit and offset"""
        return await self.file_repository.get_all(offset, limit)

    async def get_file(
        self,
        file_id: str,
    ):
        """Get file by file_id, will fail if multiple or none files are found"""
        file = await self.file_repository.get_by_id(file_id)
        if file is None:
            raise HTTPException(status_code=404, detail=f"{File.__name__} not found")
        return GetFileResponse.from_db_model(file)

    async def create_presigned_url(
        self,
        create_presigned_url_request: CreatePresignedUrlRequest,
        postgres_session: AsyncSession,
        s3_client: S3Client,
    ):
        """Creates a presigned URL and track it inside the database"""
        # TODO In the future replace first UUID with the 'user'
        object_key = f"{uuid4()}/{uuid4()}/{create_presigned_url_request.file_name}"
        presigned_url: str = await s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": object_key,
                "ContentType": create_presigned_url_request.mime_type.value,
                "ContentLength": create_presigned_url_request.file_size,
            },
            ExpiresIn=3600,
        )

        file_data = FileCreate(
            file_name=create_presigned_url_request.file_name,
            mime_type=create_presigned_url_request.mime_type,
            file_size=create_presigned_url_request.file_size,
            bucket_name=settings.S3_BUCKET,
            object_key=object_key,
        )

        file = await self.file_repository.create(file_data)

        await postgres_session.commit()
        await postgres_session.refresh(file)

        return {
            "presigned_url": presigned_url,
            "file_id": file.id,
            "object_key": object_key,
        }

    async def delete_file_mark(
        self,
        file_id: str,
        postgres_session: AsyncSession,
    ):
        """Sets file status as delete, marking it for eventual deletion"""
        file_deleted = await self.file_repository.update_file_status(
            file_id, FileStatus.DELETED
        )
        if not file_deleted:
            raise HTTPException(status_code=404, detail=f"{File.__name__} not found")
        await postgres_session.commit()

        return {"message": "File deleted successfully", "file_id": file_id}

    async def delete_file(
        self,
        file_id: str,
        postgres_session: AsyncSession,
    ):
        """Deletes file from postgres DB"""
        file_deleted = await self.file_repository.delete(file_id)
        if not file_deleted:
            raise HTTPException(status_code=404, detail=f"{File.__name__} not found")
        await postgres_session.commit()
        return {"message": "File deleted successfully", "file_id": file_id}
