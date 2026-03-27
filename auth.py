import os
import secrets
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# Consistency with Cloud API
API_KEY = os.getenv("MASTER_MONITOR_API_KEY")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """
    Ensures only devices/users with the correct key can post to the gateway.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Include 'X-API-Key' header.",
        )
    if not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key.",
        )
    return api_key
