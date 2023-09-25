# -*- coding: utf-8 -*-
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic.generics import GenericModel

from wyvern.entities.identifier import Identifier
from wyvern.exceptions import WyvernModelInputError
from wyvern.wyvern_typing import GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY

MODEL_OUTPUT_DATA_TYPE = TypeVar(
    "MODEL_OUTPUT_DATA_TYPE",
    bound=Union[
        float,
        str,
        List[float],
        Dict[str, Any],
    ],
)
"""
MODEL_OUTPUT_DATA_TYPE is the type of the output of the model. It can be a float, a string, or a list of floats
(e.g. a list of probabilities, embeddings, etc.)
"""


class ModelOutput(GenericModel, Generic[MODEL_OUTPUT_DATA_TYPE]):
    """
    This class defines the output of a model.

    Args:
        data: A dictionary mapping entity identifiers to model outputs. The model outputs can also be None.
        model_name: The name of the model. This is optional.
    """

    data: Dict[Identifier, Optional[MODEL_OUTPUT_DATA_TYPE]]
    model_name: Optional[str] = None

    def get_entity_output(
        self,
        identifier: Identifier,
    ) -> Optional[MODEL_OUTPUT_DATA_TYPE]:
        """
        Get the model output for a given entity identifier.

        Args:
            identifier: The identifier of the entity.

        Returns:
            The model output for the given entity identifier. This can also be None if the model output is None.
        """
        return self.data.get(identifier)


class ModelInput(GenericModel, Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY]):
    """
    This class defines the input to a model.

    Args:
        request: The request that will be used to generate the model input.
        entities: A list of entities that will be used to generate the model input.
    """

    request: REQUEST_ENTITY
    entities: List[GENERALIZED_WYVERN_ENTITY] = []

    @property
    def first_entity(self) -> GENERALIZED_WYVERN_ENTITY:
        """
        Get the first entity in the list of entities. This is useful when you know that there is only one entity.

        Returns:
            The first entity in the list of entities.
        """
        if not self.entities:
            raise WyvernModelInputError(model_input=self)
        return self.entities[0]

    @property
    def first_identifier(self) -> Identifier:
        """
        Get the identifier of the first entity in the list of entities. This is useful when you know that there is only
        one entity.

        Returns:
            The identifier of the first entity in the list of entities.
        """
        return self.first_entity.identifier


MODEL_INPUT = TypeVar("MODEL_INPUT", bound=ModelInput)
MODEL_OUTPUT = TypeVar("MODEL_OUTPUT", bound=ModelOutput)


class ChainedModelInput(ModelInput, Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY]):
    upstream_model_output: Dict[
        Identifier,
        Optional[
            Union[
                float,
                str,
                List[float],
                Dict[str, Optional[Union[float, str, list[float]]]],
            ]
        ],
    ]
    upstream_model_name: Optional[str] = None
