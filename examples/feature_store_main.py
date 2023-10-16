# -*- coding: utf-8 -*-
import logging
from typing import Dict

import typer
from pydantic import BaseModel

from wyvern import Identifier
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
        feature_df = await feature_store_retrieval_component.execute(input)
        feature_dicts = feature_df.df.to_dicts()
        feature_data: Dict[str, FeatureData] = {
            str(feature_dict["IDENTIFIER"]): FeatureData(
                identifier=Identifier(
                    identifier_type=feature_dict["IDENTIFIER"].split("::")[0],
                    identifier=feature_dict["IDENTIFIER"].split("::")[1],
                ),
                features={
                    feature_name: feature_value
                    for feature_name, feature_value in feature_dict.items()
                    if feature_name != "IDENTIFIER"
                },
            )
            for feature_dict in feature_dicts
        }
        return FeatureStoreResponse(
            feature_data=feature_data,
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
