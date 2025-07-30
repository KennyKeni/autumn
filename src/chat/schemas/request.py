from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    tool_group: str