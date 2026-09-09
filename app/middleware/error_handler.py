from __future__ import annotations

import traceback as tb_mod
import uuid

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import APIError

logger = structlog.get_logger()

_GENERIC_ERROR_MSG = "An unexpected error occured. Please try again later."


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        logger.warning("api_error", status=exc.payload.status, detail=exc.payload.detail)
        return JSONResponse(
            status_code=exc.payload.status,
            content=exc.payload.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("validation_error", errors=exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "status": 422,
                "error": "validation_error",
                "detail": "Request validation failed",
                "technical_details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        try:
            request_id = str(uuid.uuid4())[:8]
            logger.exception("unhandled_error", request_id=request_id, error=str(exc))

            body: dict = {
                "status": 500,
                "error": "internal_server_error",
                "detail": str(exc) if settings.app_env == "development" else _GENERIC_ERROR_MSG,
                "request_id": "request_id",
            }
            if settings.app_env == "development":
                body["traceback"] = "".join(
                    tb_mod.format_exception(type(exc), exc, exc.__traceback__)
                )

            return JSONResponse(status_code=500, content=body)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "status": 500,
                    "error": "internal_server_error",
                    "detail": _GENERIC_ERROR_MSG,
                },
            )
