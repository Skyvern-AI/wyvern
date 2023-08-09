# -*- coding: utf-8 -*-
import asyncio
import logging
from functools import cached_property
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeAlias,
    Union,
    get_args,
)

from wyvern.components.models.model_component import (
    MODEL_INPUT,
    MODEL_OUTPUT,
    ModelComponent,
)
from wyvern.config import settings
from wyvern.core.httpx import httpx_client
from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import WyvernEntity
from wyvern.entities.request import BaseWyvernRequest
from wyvern.exceptions import (
    WyvernModelbitTokenMissingError,
    WyvernModelbitValidationError,
)

JSON: TypeAlias = Union[Dict[str, "JSON"], List["JSON"], str, int, float, bool, None]
logger = logging.getLogger(__name__)


class ModelbitComponent(ModelComponent[MODEL_INPUT, MODEL_OUTPUT]):
    AUTH_TOKEN: str = ""
    URL: str = ""

    def __init__(
        self,
        *upstreams,
        name: Optional[str] = None,
        auth_token: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        super().__init__(*upstreams, name=name)
        self._auth_token = auth_token or self.AUTH_TOKEN
        self._modelbit_url = url or self.URL
        self.headers = {
            "Authorization": self._auth_token,
            "Content-Type": "application/json",
        }

        # TODO shu: test out the model_input_type
        self.model_input_type = self.get_type_args_simple(0)
        self.model_output_type = self.get_type_args_simple(1)

        if not self._auth_token:
            raise WyvernModelbitTokenMissingError()

    @cached_property
    def modelbit_features(self) -> List[str]:
        return []

    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        return set(self.modelbit_features)

    @classmethod
    def get_type_args_simple(cls, index: int) -> Type:
        return get_args(cls.__orig_bases__[0])[index]  # type: ignore

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
        all_requests = [
            [
                idx + 1,
                [
                    self.get_feature(identifier, feature_name)
                    for feature_name in self.modelbit_features
                ],
            ]
            for idx, identifier in enumerate(target_identifiers)
        ]
        return target_identifiers, all_requests

    async def inference(self, input: MODEL_INPUT, **kwargs) -> MODEL_OUTPUT:
        # TODO shu: currently we don't support modelbit inference just for request if the input contains entities

        target_identifiers, all_requests = await self.build_requests(input)

        if len(target_identifiers) != len(all_requests):
            raise WyvernModelbitValidationError(
                f"Number of identifiers ({len(target_identifiers)}) "
                f"does not match number of modelbit requests ({len(all_requests)})",
            )

        # split requests into smaller batches and parallelize them
        futures = [
            httpx_client().post(
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
            if resp.status_code != 200:
                logger.warning(f"Modelbit inference failed: {resp.text}")
                continue
            resp_list: List[
                List[Union[float, str, List[float], None]]
            ] = resp.json().get(
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
