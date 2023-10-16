# -*- coding: utf-8 -*-
import asyncio
import logging
from functools import cached_property
from typing import Any, Dict, List, Optional, Set, Tuple, TypeAlias, Union, final

from wyvern.components.models.model_component import (
    BaseModelComponent,
    MultiEntityModelComponent,
    SingleEntityModelComponent,
)
from wyvern.config import settings
from wyvern.core.http import aiohttp_client
from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import WyvernEntity
from wyvern.entities.model_entities import MODEL_INPUT, MODEL_OUTPUT
from wyvern.entities.request import BaseWyvernRequest
from wyvern.exceptions import (
    WyvernModelbitTokenMissingError,
    WyvernModelbitValidationError,
)
from wyvern.wyvern_typing import INPUT_TYPE, REQUEST_ENTITY

JSON: TypeAlias = Union[Dict[str, "JSON"], List["JSON"], str, int, float, bool, None]
logger = logging.getLogger(__name__)


class ModelbitMixin(BaseModelComponent[INPUT_TYPE, MODEL_OUTPUT]):
    AUTH_TOKEN: str = ""
    URL: str = ""

    def __init__(
        self,
        *upstreams,
        name: Optional[str] = None,
        auth_token: Optional[str] = None,
        url: Optional[str] = None,
        cache_output: bool = False,
    ) -> None:
        """
        Args:
            *upstreams: A list of upstream components.
            name: A string that represents the name of the model.
            auth_token: A string that represents the auth token for Modelbit.
            url: A string that represents the url for Modelbit.

        Raises:
            WyvernModelbitTokenMissingError: If the auth token is not provided.
        """
        super().__init__(*upstreams, name=name, cache_output=cache_output)
        self._auth_token = auth_token or self.AUTH_TOKEN
        self._modelbit_url = url or self.URL
        self.headers = {
            "Authorization": self._auth_token,
            "Content-Type": "application/json",
        }

        if not self._auth_token:
            raise WyvernModelbitTokenMissingError()

    @cached_property
    def modelbit_features(self) -> List[str]:
        """
        This is a cached property that returns a list of modelbit features. This method should be implemented by the
        subclass.
        """
        return []

    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        """
        This is a cached property that returns a set of manifest feature names. This method wraps around the
        modelbit_features property.
        """
        return set(self.modelbit_features)

    async def inference(self, input: INPUT_TYPE, **kwargs) -> MODEL_OUTPUT:
        """
        This method sends a request to Modelbit and returns the output.
        """
        # TODO shu: currently we don't support modelbit inference just for request if the input contains entities

        target_identifiers, all_requests = await self.build_requests(input)

        if len(target_identifiers) != len(all_requests):
            raise WyvernModelbitValidationError(
                f"Number of identifiers ({len(target_identifiers)}) "
                f"does not match number of modelbit requests ({len(all_requests)})",
            )

        # split requests into smaller batches and parallelize them
        futures = [
            aiohttp_client().post(
                self._modelbit_url,
                headers=self.headers,
                json={"data": all_requests[i : i + settings.MODELBIT_BATCH_SIZE]},
            )
            for i in range(0, len(all_requests), settings.MODELBIT_BATCH_SIZE)
        ]
        responses = await asyncio.gather(*futures)
        # resp_list: List[List[float]] = resp.json().get("data", [])
        output_data: Dict[Identifier, Optional[Union[float, str, List[float]]]] = {}

        for batch_idx, resp in enumerate(responses):
            if resp.status != 200:
                text = await resp.text()
                logger.warning(f"Modelbit inference failed: {text}")
                continue
            resp_list: List[List[Union[float, str, List[float], None]]] = (
                await resp.json()
            ).get(
                "data",
                [],
            )
            for idx, individual_output in enumerate(resp_list):
                # individual_output[0] is the index of modelbit output which is useless so we'll not use it
                # individual_output[1] is the actual output
                output_data[
                    target_identifiers[batch_idx * settings.MODELBIT_BATCH_SIZE + idx]
                ] = individual_output[1]

        return self.model_output_type(
            data=output_data,
            model_name=self.name,
        )

    async def build_requests(
        self,
        input: INPUT_TYPE,
    ) -> Tuple[List[Identifier], List[Any]]:
        """
        This method builds requests for Modelbit. This method should be implemented by the subclass.
        """
        raise NotImplementedError


class ModelbitComponent(
    ModelbitMixin[MODEL_INPUT, MODEL_OUTPUT],
    MultiEntityModelComponent[MODEL_INPUT, MODEL_OUTPUT],
):
    """
    ModelbitComponent is a base class for all modelbit model components. It provides a common interface to implement
    all modelbit models.

    ModelbitComponent is a subclass of ModelComponent.

    Attributes:
        AUTH_TOKEN: A class variable that stores the auth token for Modelbit.
        URL: A class variable that stores the url for Modelbit.
    """

    async def build_requests(
        self,
        input: MODEL_INPUT,
    ) -> Tuple[List[Identifier], List[Any]]:
        """
        Please refer to modlebit batch inference API:
            https://doc.modelbit.com/deployments/rest-api/
        """
        target_entities: List[
            Union[WyvernEntity, BaseWyvernRequest]
        ] = input.entities or [input.request]
        target_identifiers = [entity.identifier for entity in target_entities]
        identifier_features_tuples = self.get_features(
            target_identifiers,
            self.modelbit_features,
        )

        all_requests = [
            [idx + 1, features]
            for idx, (identifier, features) in enumerate(identifier_features_tuples)
        ]
        return target_identifiers, all_requests


class SingleEntityModelbitComponent(
    ModelbitMixin[REQUEST_ENTITY, MODEL_OUTPUT],
    SingleEntityModelComponent[REQUEST_ENTITY, MODEL_OUTPUT],
):
    @final
    async def build_requests(
        self,
        input: REQUEST_ENTITY,
    ) -> Tuple[List[Identifier], List[Any]]:
        target_identifier, request = await self.build_request(input)
        all_requests = [[1, request]]
        return [target_identifier], all_requests

    async def build_request(self, input: REQUEST_ENTITY) -> Tuple[Identifier, Any]:
        raise NotImplementedError
