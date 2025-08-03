from fastapi import APIRouter

from src.chat.dependencies import ChatServiceDep
from src.chat.schemas.request import ChatRequest
from src.partitions.dependencies import ValidPartitionLoadedDep

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{partition_id}")
async def chat(
    chat_request: ChatRequest,
    partition: ValidPartitionLoadedDep,
    chat_service: ChatServiceDep,
):
    return await chat_service.basic_query(chat_request, partition)
