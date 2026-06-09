import os
from fastapi import Header, HTTPException, status

_API_KEY = os.getenv("API_SECRET_KEY", "changeme")


async def require_auth(x_api_key: str = Header(..., alias="X-API-Key")) -> dict:
    if x_api_key != _API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return {"key": x_api_key}
