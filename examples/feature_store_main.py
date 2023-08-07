# -*- coding: utf-8 -*-
import logging
from typing import Dict

import typer
from pydantic import BaseModel

from wyvern.components.api_route_component import APIRouteComponent
from wyvern.components.features.feature_store import (
    FeatureStoreRetrievalRequest,
    feature_store_retrieval_component,
)
from wyvern.entities.feature_entities import FeatureData
from wyvern.service import WyvernService

wyvern_cli_app = typer.Typer()

logger = logging.getLogger(__name__)


class FeatureStoreResponse(BaseModel):
    feature_data: Dict[str, FeatureData]


class FeatureStoreTestingComponent(
    APIRouteComponent[FeatureStoreRetrievalRequest, FeatureStoreResponse],
):
    PATH = "/feature-store-testing"
    REQUEST_SCHEMA_CLASS = FeatureStoreRetrievalRequest
    RESPONSE_SCHEMA_CLASS = FeatureStoreResponse

    async def execute(
        self, input: FeatureStoreRetrievalRequest, **kwargs
    ) -> FeatureStoreResponse:
        logger.info(f"Executing input {input}")
        feature_map = await feature_store_retrieval_component.execute(input)

        return FeatureStoreResponse(
            feature_data={
                identifier.identifier: feature_map.feature_map[identifier]
                for identifier in feature_map.feature_map.keys()
            },
        )


@wyvern_cli_app.command()
def run(
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """
    Run your wyvern service
    """
    WyvernService.run(
        route_components=[FeatureStoreTestingComponent],
        host=host,
        port=port,
    )


if __name__ == "__main__":
    # TODO (suchintan): Add support for hot swapping code here
    wyvern_cli_app()
