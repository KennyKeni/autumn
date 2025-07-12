from fastapi import APIRouter, Query

from src.dependencies import PostgresDep, S3ClientDep
from src.files.dependencies import FileServiceDep
from src.files.schemas.requests import CreatePresignedUrlRequest


router = APIRouter(prefix="/files", tags=["files"])


# TODO This should be very very limited
@router.get("")
async def get_all_file(
    file_service: FileServiceDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
):
    return await file_service.get_all(offset, limit)


@router.get("/{file_id}")
async def get_file(
    file_id: str,
    file_service: FileServiceDep,
):
    return await file_service.get_file(file_id)


@router.post("/presigned")
async def create_presigned_url(
    request: CreatePresignedUrlRequest,
    postgres_session: PostgresDep,
    s3_client: S3ClientDep,
    file_service: FileServiceDep,
):
    return await file_service.create_presigned_url(request, postgres_session, s3_client)


@router.put("/presigned/confirm/{file_id}")
async def confirm_presigned_upload(
    file_id: str,
    postgres_session: PostgresDep,
    file_service: FileServiceDep,
):
    return await file_service.confirm_upload(file_id, postgres_session)


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    postgres_session: PostgresDep,
    file_service: FileServiceDep,
):
    return await file_service.delete_file_mark(file_id, postgres_session)
