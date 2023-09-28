# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from datetime import datetime
from typing import Generic, List, Optional, Sequence

from ddtrace import tracer
from pydantic.generics import GenericModel

from wyvern import request_context
from wyvern.components.component import Component
from wyvern.components.events.events import EntityEventData, EventType, LoggedEvent
from wyvern.components.helpers.sorting import SortingComponent
from wyvern.entities.candidate_entities import (
    GENERALIZED_WYVERN_ENTITY,
    ScoredCandidate,
)
from wyvern.entities.identifier import Identifier
from wyvern.entities.model_entities import MODEL_OUTPUT_DATA_TYPE
from wyvern.event_logging import event_logger
from wyvern.wyvern_typing import REQUEST_ENTITY

logger = logging.getLogger(__name__)


class BusinessLogicEventData(EntityEventData):
    """
    The data associated with a business logic event

    Parameters:
        business_logic_pipeline_order: The order of the business logic pipeline that this event occurred in
        business_logic_name: The name of the business logic component that this event occurred in
        old_score: The old score of the entity
        new_score: The new score of the entity
    """

    business_logic_pipeline_order: int
    business_logic_name: str
    old_score: str
    new_score: str


class BusinessLogicEvent(LoggedEvent[BusinessLogicEventData]):
    """
    An event that occurs in the business logic layer
    """

    event_type: EventType = EventType.BUSINESS_LOGIC


class BusinessLogicRequest(
    GenericModel,
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    """
    A request to the business logic layer to perform business logic on a set of candidates

    Parameters:
        request: The request that the business logic layer is being asked to perform business logic on
        scored_candidates: The candidates that the business logic layer is being asked to perform business logic on
    """

    request: REQUEST_ENTITY
    scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]] = []


class SingleEntityBusinessLogicRequest(
    GenericModel,
    Generic[REQUEST_ENTITY, MODEL_OUTPUT_DATA_TYPE],
):
    """
    A request to the business logic layer to perform business logic on a single candidate

    Parameters:
        request: The request that the business logic layer is being asked to perform business logic on
        candidate: The candidate that the business logic layer is being asked to perform business logic on
    """

    identifier: Identifier
    request: REQUEST_ENTITY
    model_output: Optional[MODEL_OUTPUT_DATA_TYPE] = None


# TODO (suchintan): Possibly delete this now that events are gone
class BusinessLogicResponse(
    GenericModel,
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    """
    The response from the business logic layer after performing business logic on a set of candidates

    Parameters:
        request: The request that the business logic layer was asked to perform business logic on
        adjusted_candidates: The candidates that the business logic layer performed business logic on
    """

    request: BusinessLogicRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY]
    adjusted_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]


class SingleEntityBusinessLogicResponse(
    GenericModel,
    Generic[REQUEST_ENTITY, MODEL_OUTPUT_DATA_TYPE],
):
    """
    The response from the business logic layer after performing business logic on a single candidate

    Parameters:
        request: The request that the business logic layer was asked to perform business logic on
        adjusted_candidate: The candidate that the business logic layer performed business logic on
    """

    request: REQUEST_ENTITY
    adjusted_output: Optional[MODEL_OUTPUT_DATA_TYPE] = None


class BusinessLogicComponent(
    Component[
        BusinessLogicRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
    ],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    """
    A component that performs business logic on an entity with a set of candidates

    The request itself could contain more than just entities, for example it may contain a query and so on
    """

    pass


class SingleEntityBusinessLogicComponent(
    Component[
        SingleEntityBusinessLogicRequest[
            REQUEST_ENTITY,
            MODEL_OUTPUT_DATA_TYPE,
        ],
        MODEL_OUTPUT_DATA_TYPE,
    ],
    Generic[REQUEST_ENTITY, MODEL_OUTPUT_DATA_TYPE],
):
    """
    A component that performs business logic on an entity with a set of candidates

    The request itself could contain more than just entities, for example it may contain a query and so on
    """

    pass


class BusinessLogicPipeline(
    Component[
        BusinessLogicRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        BusinessLogicResponse[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
    ],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    """
    Steps through a series of business logic components and returns the final output

    This operation is fully chained, meaning that the output of each business logic component is passed
        as an input to the next business logic component
    """

    def __init__(
        self,
        *upstreams: BusinessLogicComponent[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        name: Optional[str] = None,
    ):
        self.ordered_upstreams = upstreams
        self.sorting_component: SortingComponent = SortingComponent(
            name="business_logic_sorting",
        )
        super().__init__(self.sorting_component, *upstreams, name=name)

    @tracer.wrap(name="BusinessLogicPipeline.execute")
    async def execute(
        self,
        input: BusinessLogicRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        **kwargs,
    ) -> BusinessLogicResponse[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY]:
        """
        Executes the business logic pipeline on the inputted candidates

        Parameters:
            input: The input to the business logic pipeline

        Returns:
            The output of the business logic pipeline
        """
        argument = input

        # Make sure that the input candidates are actually sorted
        output = await self.sorting_component.execute(input.scored_candidates)

        for (pipeline_index, upstream) in enumerate(self.ordered_upstreams):
            old_scores = [candidate.score for candidate in argument.scored_candidates]

            # this output might have the same reference as the argument.scored_candidates
            output = await upstream.execute(input=argument, **kwargs)

            # TODO (suchintan): This currently assumes that the
            #  output order is unchanged by the business logic component
            #  This is not necessarily true, so we should fix this in the future

            # TODO (suchintan): Make this properly async -- right now it's fast enough
            # where we don't have to care, but in the future we might
            extracted_events: List[
                BusinessLogicEvent
            ] = self.extract_business_logic_events(
                output,
                pipeline_index,
                upstream.name,
                argument.request.request_id,
                old_scores,
            )

            def log_events(
                extracted_events: List[BusinessLogicEvent] = extracted_events,
            ):
                return extracted_events

            # TODO (suchintan): "invariant" list error
            event_logger.log_events(log_events)  # type: ignore
            output = await self.sorting_component.execute(output)

            argument = BusinessLogicRequest(
                request=input.request,
                scored_candidates=output,
            )

        return BusinessLogicResponse(
            request=input,
            adjusted_candidates=output,
        )

    def extract_business_logic_events(
        self,
        output: Sequence[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        pipeline_index: int,
        upstream_name: str,
        request_id: str,
        old_scores: List,
    ) -> List[BusinessLogicEvent]:
        """
        Extracts the business logic events from the output of a business logic component

        Args:
            output: The output of a business logic component
            pipeline_index: The index of the business logic component in the business logic pipeline
            upstream_name: The name of the business logic component
            request_id: The request id of the request that the business logic component was called in
            old_scores: The old scores of the candidates that the business logic component was called on

        Returns:
            The business logic events that were extracted from the output of the business logic component
        """
        timestamp = datetime.utcnow()
        events = [
            BusinessLogicEvent(
                request_id=request_id,
                api_source=request_context.ensure_current_request().url_path,
                event_timestamp=timestamp,
                event_data=BusinessLogicEventData(
                    business_logic_pipeline_order=pipeline_index,
                    business_logic_name=upstream_name,
                    old_score=str(old_scores[j]),
                    new_score=str(output[j].score),
                    entity_identifier=candidate.entity.identifier.identifier,
                    entity_identifier_type=candidate.entity.identifier.identifier_type,
                ),
            )
            for (j, candidate) in enumerate(output)
            if output[j].score != old_scores[j]
        ]

        return events


class SingleEntityBusinessLogicPipeline(
    Component[
        SingleEntityBusinessLogicRequest[
            REQUEST_ENTITY,
            MODEL_OUTPUT_DATA_TYPE,
        ],
        SingleEntityBusinessLogicResponse[
            REQUEST_ENTITY,
            MODEL_OUTPUT_DATA_TYPE,
        ],
    ],
    Generic[REQUEST_ENTITY, MODEL_OUTPUT_DATA_TYPE],
):
    def __init__(
        self,
        *upstreams: SingleEntityBusinessLogicComponent[
            REQUEST_ENTITY,
            MODEL_OUTPUT_DATA_TYPE,
        ],
        name: Optional[str] = None,
    ):
        self.ordered_upstreams = upstreams
        super().__init__(*upstreams, name=name)

    async def execute(
        self,
        input: SingleEntityBusinessLogicRequest[
            REQUEST_ENTITY,
            MODEL_OUTPUT_DATA_TYPE,
        ],
        **kwargs,
    ) -> SingleEntityBusinessLogicResponse[REQUEST_ENTITY, MODEL_OUTPUT_DATA_TYPE]:
        argument = input
        for (pipeline_index, upstream) in enumerate(self.ordered_upstreams):
            old_output = str(argument.model_output)

            output = await upstream.execute(argument, **kwargs)
            extracted_events: List[
                BusinessLogicEvent
            ] = self.extract_business_logic_events(
                input.identifier,
                str(output),
                old_output,
                pipeline_index,
                upstream.name,
                input.request.request_id,
            )

            def log_events(
                extracted_events: List[BusinessLogicEvent] = extracted_events,
            ):
                return extracted_events

            event_logger.log_events(log_events)  # type: ignore

            argument = SingleEntityBusinessLogicRequest[
                REQUEST_ENTITY,
                MODEL_OUTPUT_DATA_TYPE,
            ](
                identifier=input.identifier,
                request=input.request,
                model_output=output,
            )

        return SingleEntityBusinessLogicResponse(
            request=input.request,
            adjusted_output=argument.model_output,
        )

    def extract_business_logic_events(
        self,
        identifier: Identifier,
        output: str,
        old_output: str,
        pipeline_index: int,
        upstream_name: str,
        request_id: str,
    ) -> List[BusinessLogicEvent]:
        """
        Extracts the business logic events from the output of a business logic component

        Args:
            identifier: The identifier of the entity that the describe what the model output is for
            output: The output of a business logic component
            old_output: The old scores of the candidates that the business logic component was called on
            pipeline_index: The index of the business logic component in the business logic pipeline
            upstream_name: The name of the business logic component
            request_id: The request id of the request that the business logic component was called in

        Returns:
            The business logic events that were extracted from the output of the business logic component
        """
        timestamp = datetime.utcnow()
        events = [
            BusinessLogicEvent(
                request_id=request_id,
                api_source=request_context.ensure_current_request().url_path,
                event_timestamp=timestamp,
                event_data=BusinessLogicEventData(
                    business_logic_pipeline_order=pipeline_index,
                    business_logic_name=upstream_name,
                    old_score=old_output,
                    new_score=output,
                    entity_identifier=identifier.identifier,
                    entity_identifier_type=identifier.identifier_type,
                ),
            ),
        ]

        return events
