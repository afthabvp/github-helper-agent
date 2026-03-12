from pydantic import BaseModel
from typing import Any


class TextPart(BaseModel):
    type: str = "text"
    text: str


class MessageContent(BaseModel):
    messageId: str
    role: str
    parts: list[TextPart]


class MessageParams(BaseModel):
    id: str
    message: MessageContent


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: MessageParams


class ArtifactPart(BaseModel):
    type: str = "text"
    text: str


class Artifact(BaseModel):
    parts: list[ArtifactPart]


class JsonRpcResult(BaseModel):
    artifacts: list[Artifact]


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: JsonRpcResult


class JsonRpcErrorDetail(BaseModel):
    code: int
    message: str


class JsonRpcErrorResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    error: JsonRpcErrorDetail
