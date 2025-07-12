from fastapi import APIRouter

from src.collections.dependencies import CollectionServiceDep
from src.collections.schemas.request import CreateCollectionRequest
from src.collections.schemas.response import CollectionResponse
from src.dependencies import PostgresDep, QdrantDep


router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("")
async def CreateCollection(
    request: CreateCollectionRequest,
    qdrant_client: QdrantDep,
    session: PostgresDep,
    collection_service: CollectionServiceDep,
) -> CollectionResponse:
    return await collection_service.create_collection(request, qdrant_client, session)


@router.delete("/{collection_id}")
async def DeleteCollection(
    collection_id: str,
    qdrant_client: QdrantDep,
    session: PostgresDep,
    collection_service: CollectionServiceDep,
):
    return await collection_service.delete_collection(
        collection_id, qdrant_client, session
    )
