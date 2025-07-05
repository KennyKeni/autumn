from fastapi import APIRouter

from src.dependencies import PostgresDep, S3ClientDep
from src.files.dependencies import FileServiceDep
from src.files.schemas.requests import CreatePresignedUrlRequest


router = APIRouter(prefix="/files", tags=["files"])

@router.post("/presigned")
async def create_presigned_url(
    request: CreatePresignedUrlRequest,
    postgres_session: PostgresDep,
    s3_client: S3ClientDep,
    file_service: FileServiceDep,
):
    return await file_service.create_presigned_url(request, postgres_session, s3_client)