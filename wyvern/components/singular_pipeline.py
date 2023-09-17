# -*- coding: utf-8 -*-
from typing import Any, Generic, List, Optional

from pydantic.generics import GenericModel

from wyvern.components.business_logic.business_logic import BusinessLogicPipeline
from wyvern.components.component import Component
from wyvern.components.events.events import LoggedEvent
from wyvern.components.models.model_component import (
    SingularModelComponent,
    SingularModelInput,
)
from wyvern.components.pipeline_component import PipelineComponent
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
        business_logic: Optional[BusinessLogicPipeline] = None,
        name: Optional[str] = None,
        handle_feature_store_exceptions: bool = False,
    ) -> None:
        self.model = model
        self.business_logic = business_logic
        upstream_components = list(upstreams)
        upstream_components.append(self.model)
        if self.business_logic:
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
        entity_data = output.data.get(input.entity.identifier)
        return SingularPipelineResponse(
            data=entity_data,
            events=event_logger.get_logged_events() if input.include_events else None,
        )
