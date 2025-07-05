from dependencies import PostgresDep, S3ClientDep
from files.schemas.requests import CreatePresignedUrlRequest

from src.config import settings


class FileService:
    def __init__(self):
        pass
    
    async def create_presigned_url(
        self,
        createPresignedUrlRequest: CreatePresignedUrlRequest,
        postgres_session: PostgresDep,
        s3_client: S3ClientDep,
    ):
        object_key = ""
        async with s3_client as client:
            presigned_url: str = await client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": settings.S3_BUCKET,
                    "Key": object_key,
                    "ContentType": createPresignedUrlRequest.mime_type,
                }
            )