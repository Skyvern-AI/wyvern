# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, Callable, List

from wyvern import request_context
from wyvern.components.events.events import CustomEvent, EntityEventData, LoggedEvent


def log_events(event_generator: Callable[[], List[LoggedEvent]]):
    request_context.ensure_current_request().events.append(event_generator)


def get_logged_events() -> List[LoggedEvent[Any]]:
    return [
        event
        for event_generator in request_context.ensure_current_request().events
        for event in event_generator()
    ]


def get_logged_events_generator() -> List[Callable[[], List[LoggedEvent[Any]]]]:
    return request_context.ensure_current_request().events


def log_custom_events(events: List[EntityEventData]) -> None:
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
