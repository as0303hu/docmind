from __future__ import annotations

from typing import Any

from pydantic import BaseModel

class APIErrorPayload(BaseModel):
    status:int
    error:str ="error"
    detail:str=""
    technical_details: list |dict | str | None = None

class APIError(Exception):
    def __init__(  # Fixed: double underscores
        self,
        status: int = 500,
        error: str = "error",
        detail: str = "",
        technical_details: dict | None = None,
    ) -> None:
        self.payload = APIErrorPayload(
            status=status,
            error=error,
            detail=detail,
            technical_details=technical_details,
        )
        super().__init__(detail)
        
class NotFoundError(APIError):
    def __init__(self, detail: str = "Resource not found", **kwargs: Any) -> None: # Fixed: **kwargs
        super().__init__(status=404, error="not_found", detail=detail, **kwargs)

class ValidationError(APIError):
    def __init__(self, detail: str = "Validation failed", **kwargs: Any) -> None:
        super().__init__(status=422, error="validation_error", detail=detail, **kwargs)

class ServiceUnavailableError(APIError):
    def __init__(self,detail:str = "Service temporarily unavailable", **kwargs:Any)->None:
        super().__init__(status=503, error="service_unavailable", detail=detail,**kwargs)

class AuthenticationError(APIError):
    def __init__(self, detail:str = "Authentication required", **kwargs:Any) -> None:
        super().__init__(status=401, error="auth_error", detail=detail, **kwargs)