from app.models import (
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcErrorResponse,
    JsonRpcErrorDetail,
    JsonRpcResult,
    Artifact,
    ArtifactPart,
)
from app import llm_service


def error_response(request_id: int, code: int, message: str) -> dict:
    return JsonRpcErrorResponse(
        id=request_id,
        error=JsonRpcErrorDetail(code=code, message=message),
    ).model_dump()


def success_response(request_id: int, text: str) -> dict:
    return JsonRpcResponse(
        id=request_id,
        result=JsonRpcResult(
            artifacts=[Artifact(parts=[ArtifactPart(type="text", text=text)])]
        ),
    ).model_dump()


async def handle_rpc(request: JsonRpcRequest) -> dict:
    if request.method != "message/send":
        return error_response(request.id, -32601, f"Method not found: {request.method}")

    # Extract text from message parts
    text_parts = [p.text for p in request.params.message.parts if p.type == "text"]
    prompt = "\n".join(text_parts)

    if not prompt.strip():
        return error_response(request.id, -32602, "Empty message")

    try:
        result = await llm_service.process_message(prompt)
        return success_response(request.id, result)
    except Exception as e:
        return error_response(request.id, -32000, f"Server error: {e}")
