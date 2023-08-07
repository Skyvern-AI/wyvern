# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from functools import cached_property
from typing import Dict, Generic, List, Optional, Set, TypeVar, Union

from pydantic import BaseModel
from pydantic.generics import GenericModel

from wyvern import request_context
from wyvern.components.component import Component
from wyvern.components.events.events import EventType, LoggedEvent
from wyvern.entities.identifier import Identifier
from wyvern.event_logging import event_logger
from wyvern.exceptions import WyvernModelInputError
from wyvern.wyvern_typing import GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY

MODEL_OUTPUT_DATA_TYPE = TypeVar(
    "MODEL_OUTPUT_DATA_TYPE",
    bound=Union[float, str, List[float]],
)

logger = logging.getLogger(__name__)


class ModelEventData(BaseModel):
    model_name: str
    model_output: str
    entity_identifier: Optional[str] = None
    entity_identifier_type: Optional[str] = None


class ModelEvent(LoggedEvent[ModelEventData]):
    event_type: EventType = EventType.MODEL


class ModelOutput(GenericModel, Generic[MODEL_OUTPUT_DATA_TYPE]):
    data: Dict[Identifier, Optional[MODEL_OUTPUT_DATA_TYPE]]
    model_name: Optional[str] = None

    def get_entity_output(
        self,
        identifier: Identifier,
    ) -> Optional[MODEL_OUTPUT_DATA_TYPE]:
        return self.data.get(identifier)


class ModelInput(GenericModel, Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY]):
    request: REQUEST_ENTITY
    entities: List[GENERALIZED_WYVERN_ENTITY] = []

    @property
    def first_entity(self) -> GENERALIZED_WYVERN_ENTITY:
        if not self.entities:
            raise WyvernModelInputError(model_input=self)
        return self.entities[0]

    @property
    def first_identifier(self) -> Identifier:
        return self.first_entity.identifier


MODEL_INPUT = TypeVar("MODEL_INPUT", bound=ModelInput)
MODEL_OUTPUT = TypeVar("MODEL_OUTPUT", bound=ModelOutput)


class ModelComponent(
    Component[
        MODEL_INPUT,
        MODEL_OUTPUT,
    ],
):
    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        """
        This function defines which features are necessary for model evaluation

        Our system will automatically fetch the required features from the feature store
            to make this model evaluation possible
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is a ModelComponent. "
            "The @cached_property function `manifest_feature_names` must be "
            "implemented to define features required for the model.",
        )

    async def execute(self, input: MODEL_INPUT, **kwargs) -> MODEL_OUTPUT:
        """
        The model_name and model_score will be automatically logged
        """
        api_source = request_context.ensure_current_request().url_path
        request_id = input.request.request_id
        model_output = await self.inference(input, **kwargs)

        def events_generator() -> List[ModelEvent]:
            timestamp = datetime.utcnow()
            return [
                ModelEvent(
                    request_id=request_id,
                    api_source=api_source,
                    event_timestamp=timestamp,
                    event_data=ModelEventData(
                        model_name=model_output.model_name or self.__class__.__name__,
                        model_output=str(output),
                        entity_identifier=identifier.identifier,
                        entity_identifier_type=identifier.identifier_type,
                    ),
                )
                for identifier, output in model_output.data.items()
            ]

        event_logger.log_events(events_generator)  # type: ignore

        return model_output

    async def inference(
        self,
        input: MODEL_INPUT,
        **kwargs,
    ) -> MODEL_OUTPUT:
        raise NotImplementedError


# class EmbeddingModelComponent(
#     ModelComponent[List[INPUT_TYPE], List[Embeddings], MODEL_OUTPUT],
#     Generic[INPUT_TYPE, MODEL_OUTPUT],
# ):
#     async def execute(self, input: List[INPUT_TYPE], **kwargs) -> List[Embeddings]:
#         return await self.batch_embed(inputs=input, **kwargs)

#     async def batch_embed(self, inputs: List[INPUT_TYPE], **kwargs) -> List[Embeddings]:
#         """
#         Implement this function to get your model to embed a batch of inputs
#         You should implement this when it's more efficient to embed a batch of inputs at once
#             compared to embedding them in a loop
#         """
#         tasks = [self.embed(input=input) for input in inputs]

#         task_results = await asyncio.gather(*tasks, return_exceptions=False)

#         # TODO (suchintan): Handle exceptions in the task handler
#         return list(task_results)

#     @abstractmethod
#     async def embed(self, input: INPUT_TYPE, **kwargs) -> Embeddings:
#         """
#         Implement this function to get your model to embed a particular input
#         """
#         ...
