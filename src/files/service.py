from uuid import UUID, uuid4

from fastapi import HTTPException
from src.dependencies import PostgresDep, S3ClientDep
from src.files.constants import FileStatus
from src.files.schemas.requests import CreatePresignedUrlRequest

from src.config import settings
from src.files.models.file import File


class FileService:
    def __init__(self):
        pass


    async def create_presigned_url(
        self,
        create_presigned_url_request: CreatePresignedUrlRequest,
        postgres_session: PostgresDep,
        s3_client: S3ClientDep,
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

        file = File(
            file_name=create_presigned_url_request.file_name,
            file_size=create_presigned_url_request.file_size,
            mime_type=create_presigned_url_request.mime_type,
            bucket_name=settings.S3_BUCKET,
            object_key=object_key,
        )

        postgres_session.add(file)
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
        postgres_session: PostgresDep,
    ):
        """Sets file status as delete, marking it for eventual deletion"""
        file = await postgres_session.get(File, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        file.status = FileStatus.DELETED

        await postgres_session.commit()

        return {"file_id": file_id}


    async def delete_file(
        self,
        file_id: str,
        postgres_session: PostgresDep,
    ):
        """Deletes file from postgres DB"""
        file = await self.get_file(file_id=file_id, postgres_session=postgres_session)
        
        await postgres_session.delete(file)
        await postgres_session.commit()
        return {"message": "File deleted successfully"}
    
    async def get_file(
        self,
        file_id: str,
        postgres_session: PostgresDep,
    ):
        file = await postgres_session.get(File, file_id)
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"file": file}