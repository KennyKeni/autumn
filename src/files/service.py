from uuid import uuid4
from dependencies import PostgresDep, S3ClientDep
from files.schemas.requests import CreatePresignedUrlRequest

from src.config import settings
from src.files.models.file import File


class FileService:
    def __init__(self):
        pass
    
    async def create_presigned_url(
        self,
        createPresignedUrlRequest: CreatePresignedUrlRequest,
        postgres_session: PostgresDep,
        s3_client: S3ClientDep,
    ):
        # In the future replace first UUID with the 'user'
        object_key = f"{uuid4()}/{uuid4()}/{createPresignedUrlRequest.file_name}"
        async with s3_client as client:
            presigned_url: str = await client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": settings.S3_BUCKET,
                    "Key": object_key,
                    "ContentType": createPresignedUrlRequest.mime_type,
                }
            )

            file = File(
                file_name=createPresignedUrlRequest.file_name,
                file_type=createPresignedUrlRequest.file_size,
                mime_type=createPresignedUrlRequest.mime_type,
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