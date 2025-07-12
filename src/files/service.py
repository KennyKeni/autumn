from typing import Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3 import S3Client

from src.files.constants import FileDbStatus
from src.files.models.file import File
from src.files.repository import FileSqlRepository
from src.files.schemas.requests import CreatePresignedUrlRequest, FileCreate
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.files.schemas.responses import GetFileResponse
from src.files.exceptions import FileNotFoundError


class FileService:
    def __init__(self, file_repository: FileSqlRepository):
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
        file = await self.file_repository.get_one(file_id)
        if file is None:
            raise FileNotFoundError(file_id)
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

    async def confirm_upload(
        self,
        file_id: str,
        postgres_session: AsyncSession,
    ):
        file: Optional[File] = await self.file_repository.update_status(
            file_id, FileDbStatus.UPLOADED
        )
        if file is None:
            raise FileNotFoundError(file_id)
        await postgres_session.commit()
        return {"message": "File updated successfully", "file_id": file_id}

    # TODO If file isn't uploaded yet, this creates complex logic because of it not existing in R2 yet
    # To solve this, lower presigned TTL
    # Cleanup pending files older than 2x TTL, if pending doesn't need R2 call
    async def delete_file_mark(
        self,
        file_id: str,
        postgres_session: AsyncSession,
    ):
        """Sets file status as delete, marking it for eventual deletion"""
        file_deleted = await self.file_repository.update_status(
            file_id, FileDbStatus.DELETED
        )
        if not file_deleted:
            raise FileNotFoundError(file_id)
        await postgres_session.commit()

        return {"message": "File deleted successfully", "file_id": file_id}

    async def delete_file(
        self,
        file_id: str,
        postgres_session: AsyncSession,
        s3_client: S3Client,
    ):
        """Deletes file from postgres DB"""
        deleted_file = await self.file_repository.delete_by_id(
            file_id, skip_defaults=True
        )
        if not deleted_file:
            raise FileNotFoundError(file_id)

        # TODO Parse this output
        await s3_client.delete_object(
            Bucket=deleted_file.bucket_name, Key=deleted_file.object_key
        )

        await postgres_session.commit()
        return {"message": "File deleted successfully", "file_id": file_id}
