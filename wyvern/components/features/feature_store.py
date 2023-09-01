# -*- coding: utf-8 -*-
import logging
from typing import Dict, List, Optional

from ddtrace import tracer
from pydantic import BaseModel

from wyvern.components.component import Component
from wyvern.config import settings
from wyvern.core.http import aiohttp_client
from wyvern.entities.feature_entities import (
    FeatureData,
    FeatureMap,
    build_empty_feature_map,
)
from wyvern.entities.identifier import Identifier
from wyvern.exceptions import WyvernFeatureNameError, WyvernFeatureStoreError
from wyvern.wyvern_typing import WyvernFeature

logger = logging.getLogger(__name__)


class FeatureStoreRetrievalRequest(BaseModel):
    """
    Request to retrieve features from the feature store.

    Attributes:
        identifiers: List of identifiers for which features are to be retrieved.
        feature_names: List of feature names to be retrieved. Feature names are of the form
            `<feature_view_name>:<feature_name>`.
    """

    identifiers: List[Identifier]
    # TODO (suchintan): Feature names are currently linked to feature views..
    #  we need to make that coupling more explicit
    feature_names: List[str]


class FeatureStoreRetrievalComponent(
    Component[FeatureStoreRetrievalRequest, FeatureMap],
):
    """
    Component to retrieve features from the feature store. This component is responsible for fetching features from
    the feature store and returning them in the form of a FeatureMap. The FeatureMap is a mapping from identifiers to
    FeatureData. The FeatureData contains the identifier and a mapping from feature names to feature values. The
    feature names are of the form `<feature_view_name>:<feature_name>`. The feature values are of type WyvernFeature
    which is a union of all the possible feature types. The feature types are defined in `wyvern/wyvern_typing.py`.
    The FeatureStoreRetrievalComponent is a singleton and can be accessed via `feature_store_retrieval_component`.

    The FeatureStoreRetrievalComponent is configured via the following environment variables:
    - WYVERN_API_KEY: if you're using Wyvern's feature store, this is the API key for Wyvern
    - WYVERN_FEATURE_STORE_URL: url to the feature store
    - WYVERN_ONLINE_FEATURES_PATH: url path to the feature store's online features endpoint
    - FEATURE_STORE_ENABLED: whether the feature store is enabled or not
    """

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
        """
        Fetches features from the feature store for the given identifiers and feature names.

        Args:
            identifiers: List of identifiers for which features are to be retrieved.
            feature_names: List of feature names to be retrieved.

        Returns:
            FeatureMap containing the features for the given identifiers and feature names.
        """
        if not feature_names or not settings.FEATURE_STORE_ENABLED:
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
        response = await aiohttp_client().post(
            f"{self.feature_store_host}{settings.WYVERN_ONLINE_FEATURES_PATH}",
            headers=self.request_headers,
            json=request_body,
        )

        if response.status != 200:
            resp_text = await response.text()
            logger.error(
                f"Error fetching features from feature store: [{response.status}] {resp_text}",
            )
            raise WyvernFeatureStoreError(error=resp_text)

        # TODO (suchintan): More graceful response handling here

        response_json = await response.json()
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

        return FeatureMap(feature_map=feature_map)

    @tracer.wrap(name="FeatureStoreRetrievalComponent.execute")
    async def execute(
        self,
        input: FeatureStoreRetrievalRequest,
        handle_exceptions: bool = False,
        **kwargs,
    ) -> FeatureMap:
        """
        Fetches features from the feature store for the given identifiers and feature names. This method is a wrapper
        around `fetch_features_from_feature_store` which handles exceptions and returns an empty FeatureMap in case of
        an exception.
        """
        # TODO (suchintan): Integrate this with Feature Store

        try:
            response = await self.fetch_features_from_feature_store(
                input.identifiers,
                input.feature_names,
            )
            return response
        except WyvernFeatureStoreError as e:
            if handle_exceptions:
                # logging is handled where the exception is raised
                return build_empty_feature_map(input.identifiers, input.feature_names)
            else:
                raise e


# TODO (suchintan): IS this the right way to define a singleton?
"""
Singleton instance of FeatureStoreRetrievalComponent. This can be accessed via `feature_store_retrieval_component`.
"""
feature_store_retrieval_component = FeatureStoreRetrievalComponent()
