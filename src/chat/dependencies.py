from typing import Annotated
from fastapi import Depends
from llama_index.llms.openai_like import OpenAILike
from llama_index.llms.openrouter import OpenRouter
from src.chat.service import ChatService
from src.config import SETTINGS
from src.dependencies import PostgresDep
from src.tools.dependencies import ToolServiceDep


def _get_llm() -> OpenRouter:
    return OpenRouter(
        model="google/gemini-2.5-flash-lite",
        temperature=0.0,
        api_key=SETTINGS.OPENROUTER_API_KEY,
        is_function_calling_model = True,
        verbose=True,
        max_tokens=512
    )

def _get_tool_llm() -> OpenRouter:
    return OpenRouter(
        # model="moonshotai/kimi-k2",
        model="qwen/qwen3-235b-a22b-07-25",
        temperature=0.0,
        api_key=SETTINGS.OPENROUTER_API_KEY,
        is_function_calling_model = True,
        verbose=True,
        max_tokens=1028,
    )

def _get_chat_service(
    llm: "LlmDep",
    tool_llm: "ToolLlmDep",
    tool_service: ToolServiceDep,
    session: PostgresDep,
) -> ChatService:
    return ChatService(
        llm=llm,
        tool_llm=tool_llm,
        tool_service=tool_service,
        session=session,
    )

LlmDep = Annotated[OpenAILike, Depends(_get_llm)]
ToolLlmDep = Annotated[OpenAILike, Depends(_get_tool_llm)]
ChatServiceDep = Annotated[ChatService, Depends(_get_chat_service)]