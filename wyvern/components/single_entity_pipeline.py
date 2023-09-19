# -*- coding: utf-8 -*-
from typing import Any, Dict, Generic, List, Optional, Union

from pydantic.generics import GenericModel

from wyvern.components.business_logic.business_logic import (
    SingleEntityBusinessLogicPipeline,
    SingleEntityBusinessLogicRequest,
)
from wyvern.components.component import Component
from wyvern.components.events.events import LoggedEvent
from wyvern.components.models.model_component import SingleEntityModelComponent
from wyvern.components.pipeline_component import PipelineComponent
from wyvern.entities.identifier import Identifier
from wyvern.entities.model_entities import MODEL_OUTPUT_DATA_TYPE
from wyvern.event_logging import event_logger
from wyvern.exceptions import MissingModeloutputError
from wyvern.wyvern_typing import REQUEST_ENTITY


class SingleEntityPipelineResponse(GenericModel, Generic[MODEL_OUTPUT_DATA_TYPE]):
    data: MODEL_OUTPUT_DATA_TYPE
    events: Optional[List[LoggedEvent[Any]]] = None


class SingleEntityPipeline(
    PipelineComponent[
        REQUEST_ENTITY,
        SingleEntityPipelineResponse[MODEL_OUTPUT_DATA_TYPE],
    ],
    Generic[REQUEST_ENTITY, MODEL_OUTPUT_DATA_TYPE],
):
    def __init__(
        self,
        *upstreams: Component,
        model: SingleEntityModelComponent,
        business_logic: Optional[SingleEntityBusinessLogicPipeline] = None,
        name: Optional[str] = None,
        handle_feature_store_exceptions: bool = False,
    ) -> None:
        self.model = model
        self.business_logic: SingleEntityBusinessLogicPipeline

        upstream_components = list(upstreams)
        upstream_components.append(self.model)
        if business_logic:
            self.business_logic = business_logic
        else:
            self.business_logic = SingleEntityBusinessLogicPipeline()
        upstream_components.append(self.business_logic)
        super().__init__(
            *upstream_components,
            name=name,
            handle_feature_store_exceptions=handle_feature_store_exceptions,
        )

    async def execute(
        self,
        input: REQUEST_ENTITY,
        **kwargs,
    ) -> SingleEntityPipelineResponse[MODEL_OUTPUT_DATA_TYPE]:
        output = await self.model.execute(input, **kwargs)
        identifiers: List[Identifier] = list(output.data.keys())
        if not identifiers:
            raise MissingModeloutputError()
        identifier = identifiers[0]
        model_output_data: Union[
            float,
            str,
            List[float],
            Dict[str, Optional[Union[float, str, list[float]]]],
        ] = output.data.get(identifier)

        business_logic_input = SingleEntityBusinessLogicRequest[
            Union[
                float,
                str,
                List[float],
                Dict[str, Optional[Union[float, str, list[float]]]],
            ],
            REQUEST_ENTITY,
        ](
            identifier=identifier,
            request=input,
            model_output=model_output_data,
        )
        business_logic_output = await self.business_logic.execute(
            input=business_logic_input,
            **kwargs,
        )
        return self.generate_response(
            input,
            business_logic_output.adjusted_model_output,
        )

    def generate_response(
        self,
        input: REQUEST_ENTITY,
        pipeline_output: MODEL_OUTPUT_DATA_TYPE,
    ) -> SingleEntityPipelineResponse[MODEL_OUTPUT_DATA_TYPE]:
        return SingleEntityPipelineResponse[MODEL_OUTPUT_DATA_TYPE](
            data=pipeline_output,
            events=event_logger.get_logged_events() if input.include_events else None,
        )
