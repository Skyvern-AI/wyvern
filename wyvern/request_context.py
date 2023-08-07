# -*- coding: utf-8 -*-
from contextvars import ContextVar
from typing import Optional

from wyvern.wyvern_request import WyvernRequest

_request_context: ContextVar[Optional[WyvernRequest]] = ContextVar(
    "Global request context",
    default=None,
)


def current() -> Optional[WyvernRequest]:
    return _request_context.get()


def ensure_current_request() -> WyvernRequest:
    request = current()
    if request is None:
        raise RuntimeError("No wyvern request context")
    return request


def set(request: WyvernRequest) -> None:
    _request_context.set(request)


def reset() -> None:
    _request_context.set(None)
