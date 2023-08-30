# -*- coding: utf-8 -*-
from contextvars import ContextVar
from typing import Optional

from wyvern.wyvern_request import WyvernRequest

_request_context: ContextVar[Optional[WyvernRequest]] = ContextVar(
    "Global request context",
    default=None,
)


def current() -> Optional[WyvernRequest]:
    """
    Get the current request context

    Returns:
        The current request context, or None if there is none
    """
    return _request_context.get()


def ensure_current_request() -> WyvernRequest:
    """
    Get the current request context, or raise an error if there is none

    Returns:
        The current request context if there is one

    Raises:
        RuntimeError: If there is no current request context
    """
    request = current()
    if request is None:
        raise RuntimeError("No wyvern request context")
    return request


def set(request: WyvernRequest) -> None:
    """
    Set the current request context

    Args:
        request: The request context to set

    Returns:
        None
    """
    _request_context.set(request)


def reset() -> None:
    """
    Reset the current request context

    Returns:
        None
    """
    _request_context.set(None)
