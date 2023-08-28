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


class CandidateEventData(EntityEventData):
    """
    Event data for a candidate event

    Attributes:
        candidate_score: The score of the candidate
        candidate_order: The order of the candidate in the list of candidates
    """

    candidate_score: float
    candidate_order: int


class CandidateEvent(LoggedEvent[CandidateEventData]):
    event_type: EventType = EventType.CANDIDATE


class CandidateEventLoggingRequest(
    GenericModel,
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    request: REQUEST_ENTITY
    scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]


class CandidateEventLoggingComponent(
    Component[
        CandidateEventLoggingRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        None,
    ],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    @tracer.wrap(name="CandidateEventLoggingComponent.execute")
    async def execute(
        self,
        input: CandidateEventLoggingRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        **kwargs
    ) -> None:
        current_span = tracer.current_span()
        if current_span:
            current_span.set_tag("candidate_size", len(input.scored_candidates))
        url_path = request_context.ensure_current_request().url_path

        def candidate_events_generator() -> List[CandidateEvent]:
            timestamp = datetime.utcnow()
            candidate_events = [
                CandidateEvent(
                    request_id=input.request.request_id,
                    api_source=url_path,
                    event_timestamp=timestamp,
                    event_data=CandidateEventData(
                        entity_identifier=candidate.entity.identifier.identifier,
                        entity_identifier_type=candidate.entity.identifier.identifier_type,
                        candidate_score=candidate.score,
                        candidate_order=i,
                    ),
                )
                for i, candidate in enumerate(input.scored_candidates)
            ]
            return candidate_events

        event_logger.log_events(candidate_events_generator)  # type: ignore
