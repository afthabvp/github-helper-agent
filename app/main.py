import json
import logging
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.agent_card import AGENT_CARD
from app.auth import verify_auth
from app.models import JsonRpcRequest
from app.rpc_handler import handle_rpc, error_response

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("a2a-agent")

app = FastAPI(title="GitHub Helper A2A Agent")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/.well-known/agent.json", dependencies=[Depends(verify_auth)])
async def agent_card():
    return AGENT_CARD


@app.post("/", dependencies=[Depends(verify_auth)])
async def json_rpc(request: Request):
    try:
        body = await request.json()
        logger.info(f">>> REQUEST: {json.dumps(body, default=str)[:2000]}")
        rpc_request = JsonRpcRequest(**body)
    except Exception as e:
        logger.error(f"Invalid JSON-RPC request: {e}")
        resp = error_response(0, -32700, f"Parse error: {e}")
        logger.info(f"<<< RESPONSE (error): {json.dumps(resp, default=str)[:2000]}")
        return JSONResponse(content=resp, status_code=200)

    logger.info(f"RPC method={rpc_request.method} id={rpc_request.id}")
    result = await handle_rpc(rpc_request)
    logger.info(f"<<< RESPONSE: {json.dumps(result, default=str)[:500]}")
    return JSONResponse(content=result, status_code=200)
