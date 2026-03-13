from pydantic import BaseModel
from typing import Any, Optional, Union


class TextPart(BaseModel):
    type: str = "text"
    text: str


class MessageContent(BaseModel):
    messageId: str
    role: str
    parts: list[TextPart]


class MessageParams(BaseModel):
    id: Optional[str] = None
    message: MessageContent


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[int, str]
    method: str
    params: MessageParams


class ArtifactPart(BaseModel):
    type: str = "text"
    text: str


class Artifact(BaseModel):
    parts: list[ArtifactPart]


class TaskStatus(BaseModel):
    state: str = "completed"


class JsonRpcResult(BaseModel):
    id: str
    status: TaskStatus = TaskStatus()
    artifacts: list[Artifact]


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[int, str]
    result: JsonRpcResult


class JsonRpcErrorDetail(BaseModel):
    code: int
    message: str


class JsonRpcErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[int, str]
    error: JsonRpcErrorDetail
