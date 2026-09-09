from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant" or "tool"
    content: str


class AgentChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ToolCallRecord(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result_summary: str


class AgentChatResponse(BaseModel):
    response: str
    tools_called: List[ToolCallRecord] = []
    suggested_follow_ups: List[str] = []
