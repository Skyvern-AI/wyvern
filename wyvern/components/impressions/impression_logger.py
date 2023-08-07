# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Generic, List

from ddtrace import tracer
from pydantic.generics import GenericModel

from wyvern import request_context
from wyvern.components.component import Component
from wyvern.components.events.events import EntityEventData, EventType, LoggedEvent
from wyvern.entities.candidate_entities import (
    GENERALIZED_WYVERN_ENTITY,
    ScoredCandidate,
)
from wyvern.event_logging import event_logger
from wyvern.wyvern_typing import REQUEST_ENTITY


class ImpressionEventData(EntityEventData):
    impression_score: float
    impression_order: int


class ImpressionEvent(LoggedEvent[ImpressionEventData]):
    event_type: EventType = EventType.IMPRESSION


class ImpressionEventLoggingRequest(
    GenericModel,
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    request: REQUEST_ENTITY
    scored_impressions: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]


class ImpressionEventLoggingComponent(
    Component[
        ImpressionEventLoggingRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        None,
    ],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    @tracer.wrap(name="ImpressionEventLoggingComponent.execute")
    async def execute(
        self,
        input: ImpressionEventLoggingRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        **kwargs
    ) -> None:
        current_span = tracer.current_span()
        if current_span:
            current_span.set_tag("impression_size", len(input.scored_impressions))
        url_path = request_context.ensure_current_request().url_path

        def impression_events_generator() -> List[ImpressionEvent]:
            timestamp = datetime.utcnow()
            impression_events = [
                ImpressionEvent(
                    request_id=input.request.request_id,
                    api_source=url_path,
                    event_timestamp=timestamp,
                    event_data=ImpressionEventData(
                        entity_identifier=impression.entity.identifier.identifier,
                        entity_identifier_type=impression.entity.identifier.identifier_type,
                        impression_score=impression.score,
                        impression_order=i,
                    ),
                )
                for i, impression in enumerate(input.scored_impressions)
            ]
            return impression_events

        event_logger.log_events(impression_events_generator)  # type: ignore
