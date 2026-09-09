from __future__ import annotations

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.exceptions import AuthenticationError

_api_key_header = APIKeyHeader(name="X-API-Key",auto_error=False)

async def require_api_key(api_key:str | None = Security(_api_key_header))-> str |None:
    if not settings.require_auth:
        return None
    
    if not api_key or api_key != settings.api_key:
        raise AuthenticationError(detail="Invalid or missing API key")
    
    return api_key