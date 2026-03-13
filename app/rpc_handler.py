import uuid

from app.models import (
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcErrorResponse,
    JsonRpcErrorDetail,
    JsonRpcResult,
    TaskStatus,
    Artifact,
    ArtifactPart,
)
from app import llm_service


def error_response(request_id, code: int, message: str) -> dict:
    return JsonRpcErrorResponse(
        id=request_id,
        error=JsonRpcErrorDetail(code=code, message=message),
    ).model_dump()


def success_response(request_id, task_id: str, context_id: str, text: str) -> dict:
    return JsonRpcResponse(
        id=request_id,
        result=JsonRpcResult(
            id=task_id,
            contextId=context_id,
            status=TaskStatus(state="completed"),
            artifacts=[Artifact(
                artifactId=str(uuid.uuid4()),
                parts=[ArtifactPart(type="text", text=text)],
            )]
        ),
    ).model_dump()


SUPPORTED_METHODS = {"message/send", "tasks/send"}


async def handle_rpc(request: JsonRpcRequest) -> dict:
    if request.method not in SUPPORTED_METHODS:
        return error_response(request.id, -32601, f"Method not found: {request.method}")

    # Use task id from params if provided, otherwise generate one
    task_id = request.params.id or str(uuid.uuid4())
    context_id = str(uuid.uuid4())

    # Extract text from message parts
    text_parts = [p.text for p in request.params.message.parts if p.type == "text"]
    prompt = "\n".join(text_parts)

    if not prompt.strip():
        return error_response(request.id, -32602, "Empty message")

    try:
        result = await llm_service.process_message(prompt)
        return success_response(request.id, task_id, context_id, result)
    except Exception as e:
        return error_response(request.id, -32000, f"Server error: {e}")
