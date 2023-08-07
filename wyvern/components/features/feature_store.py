# -*- coding: utf-8 -*-
import logging
from typing import Dict, List, Optional

from ddtrace import tracer
from pydantic import BaseModel

from wyvern.components.component import Component
from wyvern.config import settings
from wyvern.core.httpx import httpx_client
from wyvern.entities.feature_entities import FeatureData, FeatureMap
from wyvern.entities.identifier import Identifier
from wyvern.exceptions import WyvernFeatureNameError, WyvernFeatureStoreError
from wyvern.wyvern_typing import WyvernFeature

logger = logging.getLogger(__name__)


class FeatureStoreRetrievalRequest(BaseModel):
    identifiers: List[Identifier]
    # TODO (suchintan): Feature names are currently linked to feature views..
    #  we need to make that coupling more explicit
    feature_names: List[str]


class FeatureStoreRetrievalComponent(
    Component[FeatureStoreRetrievalRequest, FeatureMap],
):
    def __init__(
        self,
        feature_store_host: Optional[str] = None,
        feature_store_auth_token: Optional[str] = None,
    ):
        self.feature_store_host = (
            feature_store_host or settings.WYVERN_FEATURE_STORE_URL
        )
        feature_store_auth_token = feature_store_auth_token or settings.WYVERN_API_KEY
        self.request_headers = {"x-api-key": feature_store_auth_token}

        super().__init__()

    async def fetch_features_from_feature_store(
        self,
        identifiers: List[Identifier],
        feature_names: List[str],
    ) -> FeatureMap:
        if not feature_names:
            return FeatureMap(feature_map={})

        logger.info(f"Fetching features from feature store: {feature_names}")
        invalid_feature_names: List[str] = [
            feature_name for feature_name in feature_names if ":" not in feature_name
        ]
        if invalid_feature_names:
            raise WyvernFeatureNameError(invalid_feature_names=invalid_feature_names)
        request_body = {
            "features": feature_names,
            "entities": {
                "IDENTIFIER": [identifier.identifier for identifier in identifiers],
            },
            "full_feature_names": True,
        }
        # TODO (suchintan) -- chunk + parallelize this
        # TODO (Suchintan): This is currently busted in local development
        response = await httpx_client().post(
            f"{self.feature_store_host}{settings.WYVERN_ONLINE_FEATURES_PATH}",
            headers=self.request_headers,
            json=request_body,
        )

        if response.status_code != 200:
            logger.error(f"Error fetching features from feature store: {response}")
            raise WyvernFeatureStoreError(error=response.json())

        # TODO (suchintan): More graceful response handling here

        response_json = response.json()
        feature_names = response_json["metadata"]["feature_names"]
        feature_name_keys = [
            feature_name.replace("__", ":", 1) for feature_name in feature_names
        ]

        results = response_json["results"]
        response_identifiers = results[0]["values"]

        identifier_by_identifiers = {
            identifier.identifier: identifier for identifier in identifiers
        }

        feature_map: Dict[Identifier, FeatureData] = {}
        for i in range(len(response_identifiers)):
            feature_data: Dict[str, WyvernFeature] = {
                feature_name_keys[j]: results[j]["values"][i]
                # the first feature_name is IDENTIFIER which we will skip
                for j in range(1, len(feature_names))
            }

            identifier = identifier_by_identifiers[response_identifiers[i]]
            feature_map[identifier] = FeatureData(
                identifier=identifier,
                features=feature_data,
            )

        logger.info(f"Joined feature maps: {feature_map}")
        return FeatureMap(feature_map=feature_map)

    @tracer.wrap(name="FeatureStoreRetrievalComponent.execute")
    async def execute(
        self, input: FeatureStoreRetrievalRequest, **kwargs
    ) -> FeatureMap:
        # TODO (suchintan): Integrate this with Feature Store

        response = await self.fetch_features_from_feature_store(
            input.identifiers,
            input.feature_names,
        )
        return response


# TODO (suchintan): IS this the right way to define a singleton?
feature_store_retrieval_component = FeatureStoreRetrievalComponent()
