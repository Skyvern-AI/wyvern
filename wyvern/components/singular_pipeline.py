# -*- coding: utf-8 -*-
from typing import Any, Dict, Generic, List, Optional, Union

from pydantic.generics import GenericModel

from wyvern.components.business_logic.business_logic import (
    SingularBusinessLogicPipeline,
    SingularBusinessLogicRequest,
)
from wyvern.components.component import Component
from wyvern.components.events.events import LoggedEvent
from wyvern.components.models.model_component import SingularModelComponent
from wyvern.components.pipeline_component import PipelineComponent
from wyvern.entities.candidate_entities import ScoredEntity
from wyvern.entities.model_entities import SingularModelInput
from wyvern.entities.request import BaseWyvernRequest
from wyvern.event_logging import event_logger
from wyvern.wyvern_typing import (
    GENERALIZED_WYVERN_ENTITY,
    REQUEST_ENTITY,
    RESPONSE_SCHEMA,
)


class SingularPipelineRequest(
    BaseWyvernRequest,
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    entity: GENERALIZED_WYVERN_ENTITY
    request: REQUEST_ENTITY


class SingularPipelineResponse(GenericModel, Generic[RESPONSE_SCHEMA]):
    data: RESPONSE_SCHEMA
    events: Optional[List[LoggedEvent[Any]]]


class SingularPipelineComponent(
    PipelineComponent[
        SingularPipelineRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        SingularPipelineResponse[RESPONSE_SCHEMA],
    ],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY, RESPONSE_SCHEMA],
):
    def __init__(
        self,
        *upstreams: Component,
        model: SingularModelComponent,
        business_logic: Optional[SingularBusinessLogicPipeline] = None,
        name: Optional[str] = None,
        handle_feature_store_exceptions: bool = False,
    ) -> None:
        self.model = model
        self.business_logic: SingularBusinessLogicPipeline

        upstream_components = list(upstreams)
        upstream_components.append(self.model)
        if business_logic:
            self.business_logic = business_logic
        else:
            self.business_logic = SingularBusinessLogicPipeline()
        upstream_components.append(self.business_logic)
        super().__init__(
            *upstream_components,
            name=name,
            handle_feature_store_exceptions=handle_feature_store_exceptions,
        )

    async def execute(
        self,
        input: SingularPipelineRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        **kwargs,
    ) -> SingularPipelineResponse[RESPONSE_SCHEMA]:
        model_input = SingularModelInput[
            GENERALIZED_WYVERN_ENTITY,
            SingularPipelineRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        ](
            request=input,
            entity=input.entity,
        )
        output = await self.model.execute(model_input, **kwargs)
        entity_data: Union[
            float,
            str,
            List[float],
            Dict[str, Optional[Union[float, str, list[float]]]],
        ] = output.data.get(input.entity.identifier)

        business_logic_input = SingularBusinessLogicRequest[
            GENERALIZED_WYVERN_ENTITY,
            Union[
                float,
                str,
                List[float],
                Dict[str, Optional[Union[float, str, list[float]]]],
            ],
            SingularPipelineRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        ](
            request=input,
            scored_entity=ScoredEntity(
                entity=input.entity,
                score=entity_data,
            ),
        )
        business_logic_output = await self.business_logic.execute(
            input=business_logic_input,
            **kwargs,
        )
        return SingularPipelineResponse(
            data=business_logic_output.adjusted_entity.score,
            events=event_logger.get_logged_events() if input.include_events else None,
        )
