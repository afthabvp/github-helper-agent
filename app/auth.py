import os
from fastapi import Request, HTTPException


async def verify_auth(request: Request):
    """Bearer token auth dependency. Disabled if AGENT_AUTH_TOKEN is not set."""
    expected_token = os.getenv("AGENT_AUTH_TOKEN")
    if not expected_token:
        return  # Auth disabled

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header[len("Bearer "):]
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
