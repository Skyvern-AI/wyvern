# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, Callable, List

from wyvern import request_context
from wyvern.components.events.events import (
    ENTITY_EVENT_DATA_TYPE,
    CustomEvent,
    LoggedEvent,
)


def log_events(event_generator: Callable[[], List[LoggedEvent]]):
    """
    Logs events to the current request context.

    Args:
        event_generator: A function that returns a list of events to be logged.
    """
    request_context.ensure_current_request().events.append(event_generator)


def get_logged_events() -> List[LoggedEvent[Any]]:
    """
    Returns:
        A list of all the events logged in the current request context.
    """
    return [
        event
        for event_generator in request_context.ensure_current_request().events
        for event in event_generator()
    ]


def get_logged_events_generator() -> List[Callable[[], List[LoggedEvent[Any]]]]:
    """
    Returns:
        A list of all the event generators logged in the current request context.
    """
    return request_context.ensure_current_request().events


def log_custom_events(events: List[ENTITY_EVENT_DATA_TYPE]) -> None:
    """
    Logs custom events to the current request context.

    Args:
        events: A list of custom events to be logged.
    """
    request = request_context.ensure_current_request()
    api_source = request.url_path
    request_id = request.request_id

    def event_generator() -> List[LoggedEvent[Any]]:
        timestamp = datetime.utcnow()
        return [
            CustomEvent(
                request_id=request_id,
                api_source=api_source,
                event_timestamp=timestamp,
                event_data=event,
            )
            for event in events
        ]

    request_context.ensure_current_request().events.append(event_generator)
