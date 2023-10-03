# -*- coding: utf-8 -*-
import asyncio
import logging
from datetime import datetime
from functools import cached_property
from typing import Dict, List, Optional, Sequence, Set, Type, Union, get_args

from pydantic import BaseModel

from wyvern import request_context
from wyvern.components.component import Component
from wyvern.components.events.events import EventType, LoggedEvent
from wyvern.config import settings
from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import WyvernEntity
from wyvern.entities.model_entities import MODEL_INPUT, MODEL_OUTPUT
from wyvern.entities.request import BaseWyvernRequest
from wyvern.event_logging import event_logger
from wyvern.wyvern_typing import INPUT_TYPE, REQUEST_ENTITY

logger = logging.getLogger(__name__)


class ModelEventData(BaseModel):
    """
    This class defines the data that will be logged for each model event.

    Args:
        model_name: The name of the model
        model_output: The output of the model
        entity_identifier: The identifier of the entity that was used to generate the model output. This is optional.
        entity_identifier_type: The type of the identifier of the entity that was used to generate the model output.
            This is optional.
        model_key: The key in the dictionary output.
            This attribute will only appear when the output of the model is a dictionary.
            This is optional.
    """

    model_name: str
    model_output: str
    entity_identifier: Optional[str] = None
    entity_identifier_type: Optional[str] = None
    model_key: Optional[str] = None


class ModelEvent(LoggedEvent[ModelEventData]):
    """
    Model event. This is the event that is logged when a model is evaluated.

    Args:
        event_type: The type of the event. This is always EventType.MODEL.
    """

    event_type: EventType = EventType.MODEL


class BaseModelComponent(
    Component[
        INPUT_TYPE,
        MODEL_OUTPUT,
    ],
):
    """
    This class defines a model component. A model component is a component that takes in a request and a list of
    entities and outputs a model output. The model output is a dictionary mapping entity identifiers to model outputs.
    The model outputs can also be None if the model output is None for a given entity.
    """

    def __init__(
        self,
        *upstreams,
        name: Optional[str] = None,
        cache_output: bool = False,
    ):
        super().__init__(*upstreams, name=name)
        self.model_input_type = self.get_type_args_simple(0)
        self.model_output_type = self.get_type_args_simple(1)

        self.cache_output = cache_output

    @classmethod
    def get_type_args_simple(cls, index: int) -> Type:
        """
        Get the type argument at the given index. This is used to get the model input and model output types.
        """
        return get_args(cls.__orig_bases__[0])[index]  # type: ignore

    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        """
        This function defines which features are necessary for model evaluation

        Our system will automatically fetch the required features from the feature store
            to make this model evaluation possible

        By default, a model component does not require any features, so this function returns an empty set
        """
        return set()

    async def execute(self, input: INPUT_TYPE, **kwargs) -> MODEL_OUTPUT:
        """
        The model_name and model_score will be automatically logged
        """
        wyvern_request = request_context.ensure_current_request()
        api_source = wyvern_request.url_path
        request_id = self._get_request_id(input)
        model_output = await self.inference(input, **kwargs)
        run_id = wyvern_request.run_id

        if self.cache_output:
            wyvern_request.cache_model_output(self.name, model_output.data)

        def events_generator() -> List[ModelEvent]:
            timestamp = datetime.utcnow()
            all_events: List[ModelEvent] = []
            model_name = self.name or self.__class__.__name__
            for identifier, output in model_output.data.items():
                if isinstance(output, dict):
                    for key, value in output.items():
                        all_events.append(
                            ModelEvent(
                                request_id=request_id,
                                run_id=run_id,
                                api_source=api_source,
                                event_timestamp=timestamp,
                                event_data=ModelEventData(
                                    model_name=model_name,
                                    model_output=str(value),
                                    model_key=key,
                                    entity_identifier=identifier.identifier,
                                    entity_identifier_type=identifier.identifier_type,
                                ),
                            ),
                        )
                else:
                    all_events.append(
                        ModelEvent(
                            request_id=request_id,
                            run_id=run_id,
                            api_source=api_source,
                            event_timestamp=timestamp,
                            event_data=ModelEventData(
                                model_name=model_name,
                                model_output=str(output),
                                entity_identifier=identifier.identifier,
                                entity_identifier_type=identifier.identifier_type,
                            ),
                        ),
                    )
            return all_events

        event_logger.log_events(events_generator)  # type: ignore

        return model_output

    async def inference(
        self,
        input: INPUT_TYPE,
        **kwargs,
    ) -> MODEL_OUTPUT:
        raise NotImplementedError

    def _get_request_id(self, input: INPUT_TYPE) -> Optional[str]:
        raise NotImplementedError


class MultiEntityModelComponent(BaseModelComponent[MODEL_INPUT, MODEL_OUTPUT]):
    async def batch_inference(
        self,
        request: BaseWyvernRequest,
        entities: List[Union[WyvernEntity, BaseWyvernRequest]],
    ) -> Sequence[Optional[Union[float, str, List[float]]]]:
        """
        Define your model inference in a batched manner so that it's easier to boost inference speed
        """
        raise NotImplementedError

    async def inference(
        self,
        input: MODEL_INPUT,
        **kwargs,
    ) -> MODEL_OUTPUT:
        """
        The inference function is the main entrance to model evaluation.

        By default, the base ModelComponent slices entities into smaller batches and call batch_inference on each batch.

        The default batch size is 30. You should be able to configure the MODEL_BATCH_SIZE env variable
        to change the batch size.

        In order to set up model inference, you only need to define a class that inherits ModelComponent and
        implement batch_inference.

        You can also override this function if you want to customize the inference logic.
        """
        target_entities: List[
            Union[WyvernEntity, BaseWyvernRequest]
        ] = input.entities or [input.request]

        # split entities into batches and parallelize the inferences
        batch_size = settings.MODEL_BATCH_SIZE
        futures = [
            self.batch_inference(
                request=input.request,
                entities=target_entities[i : i + batch_size],
            )
            for i in range(0, len(target_entities), batch_size)
        ]
        batch_outputs = await asyncio.gather(*futures)

        output_data: Dict[Identifier, Optional[Union[float, str, List[float]]]] = {}
        # map each entity.identifier to its output
        for batch_idx, batch_output in enumerate(batch_outputs):
            for entity_idx, output in enumerate(batch_output):
                entity = target_entities[batch_idx * batch_size + entity_idx]
                output_data[entity.identifier] = output

        return self.model_output_type(
            data=output_data,
            model_name=self.name,
        )

    def _get_request_id(self, input: MODEL_INPUT) -> Optional[str]:
        return input.request.request_id


ModelComponent = MultiEntityModelComponent


class SingleEntityModelComponent(BaseModelComponent[REQUEST_ENTITY, MODEL_OUTPUT]):
    async def inference(self, input: REQUEST_ENTITY, **kwargs) -> MODEL_OUTPUT:
        raise NotImplementedError

    def _get_request_id(self, input: REQUEST_ENTITY) -> Optional[str]:
        return input.request_id
