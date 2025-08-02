import logging
from typing import Any, Dict, List
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.objects import ObjectRetriever
from llama_index.core.tools import BaseTool
from llama_index.llms.openai_like import OpenAILike
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.chat.constant import SYSTEM_PROMPT
from src.chat.schemas.request import ChatRequest
from src.partitions.models.partition import Partition
from src.partitions.models.partition_file import PartitionFile
from src.partitions.models.partition_file_tool import PartitionFileTool
from src.tools.service import ToolService

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(
        self,
        llm: OpenAILike,
        tool_llm: OpenAILike,
        tool_service: ToolService,
        session: AsyncSession,
    ) -> None:
        self.llm = llm
        self.tool_llm = tool_llm
        self.tool_service = tool_service
        self.session = session

    async def basic_query(
        self,
        chat_request: ChatRequest,
        partition: Partition, # Must have partition_files, partition_file_tools, eager loaded
    ) -> Dict[str, Any]:
        partition_file_ids = [pf.id for pf in partition.partition_files]

        if partition_file_ids:
            await self.session.execute(
                select(PartitionFile)
                .where(PartitionFile.id.in_(partition_file_ids))
                .options(
                    selectinload(PartitionFile.partition_file_tools.and_(
                        PartitionFileTool.tool_group == chat_request.tool_group
                    )).selectinload(PartitionFileTool.partition_file).selectinload(PartitionFile.file)
                )
            )
        
        partition_files: List[PartitionFile] = partition.partition_files

        tools: List[BaseTool] = await self.tool_service.get_file_tools(partition_files, self.tool_llm)

        object_retriever: ObjectRetriever[Any] = await self.tool_service.get_object_retriever(chat_request.tool_group, partition, tools)

        agent = FunctionAgent(
            tool_retriever=object_retriever,
            llm=self.llm, 
            system_prompt = SYSTEM_PROMPT,
            verbose=True,
        )

        response: Dict[str, Any] = await agent.run(chat_request.message, max_iterations=4) # type: ignore[misc]
        
        return {"response": str(response), "debug": response} # type: ignore
