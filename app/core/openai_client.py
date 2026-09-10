#  app/core/openai_client.py
"""Shared OpenAi async client with retry logic."""

from __future__ import annotations

import asyncio
import functools
from typing import Callable, TypeVar, Awaitable, ParamSpec

from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_client: AsyncOpenAI | None=None

RETRYAPBLE_EXCEPTIONS =(APIConnectionError,APITimeoutError,RateLimitError)

T = TypeVar("T")

def get_openai_client() -> AsyncOpenAI:
    """Return a module-level singlton AsyncOpenAI client."""
    global _client
    if _client is None:
        _client =AsyncOpenAI(api_key=settings.openai_api_key)
    return _client

P = ParamSpec("P")
T = TypeVar("T")

def with_retry(
    max_retires: int = 3,
    base_delay: float=1.0,
    max_delay:float =30.0,
)-> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator for exponentional-backoff retry on transient OpenAI errors."""
    
    def decorator(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(fn)
        async def wrapper(*args,**kwargs)->T:
            last_exc: Exception | None = None
            for attempt in range(max_retires +1):
                try:
                    return await fn(*args,**kwargs)
                except RETRYAPBLE_EXCEPTIONS as exc:
                    last_exc = exc
                    if attempt == max_retires:
                        break
                    delay = min(base_delay*(2**attempt), max_delay)
                    logger.warning(
                        "openai_retry",
                        attempt = attempt+1,
                        max_retires = max_retires,
                        delay= delay,
                        error = str(exc)
                    )
                    await asyncio.sleep(delay)
            raise last_exc #type: ignore[misc]
        return wrapper
    return decorator
            