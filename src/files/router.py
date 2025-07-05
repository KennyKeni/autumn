from fastapi import APIRouter

from dependencies import CollectionBucketDep, PostgresDep
from files.schemas.requests import CreatePresignedUrlRequest


router = APIRouter(prefix="/files", tags=["files"])

@router.post("/presigned")
async def create_presigned_url(
    request: CreatePresignedUrlRequest,
    postgres_session: PostgresDep,
    s3_bucket: CollectionBucketDep,
):
    pass