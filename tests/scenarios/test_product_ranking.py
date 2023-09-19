# -*- coding: utf-8 -*-
from functools import cached_property
from typing import Any, Dict, List, Optional, Set

import pytest
import pytest_asyncio
from aioresponses import aioresponses
from fastapi.testclient import TestClient
from pydantic import BaseModel

from wyvern import request_context
from wyvern.components.features.realtime_features_component import (
    RealtimeFeatureComponent,
    RealtimeFeatureRequest,
)
from wyvern.components.models.model_component import ModelComponent
from wyvern.components.pipeline_component import PipelineComponent
from wyvern.config import settings
from wyvern.core.compression import wyvern_encode
from wyvern.core.http import aiohttp_client
from wyvern.entities.candidate_entities import CandidateSetEntity
from wyvern.entities.feature_entities import FeatureData, FeatureMap
from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import ProductEntity, WyvernEntity
from wyvern.entities.model_entities import ModelInput, ModelOutput
from wyvern.entities.request import BaseWyvernRequest
from wyvern.service import WyvernService
from wyvern.wyvern_request import WyvernRequest

PRODUCT_ENTITY_1 = {
    "product_id": "test_product1",
    "product_name": "test_product1 name",
    "product_description": "test_product1_description",
    "brand_id": "test_brand1",
}
PRODUCT_ENTITY_2 = {
    "product_id": "test_product2",
    "product_name": "test_product2 name",
    "product_description": "test_product2_description",
    "brand_id": "test_brand2",
}
PRODUCT_ENTITY_2__DUPLICATE_BRAND = {
    "product_id": "test_product2",
    "product_name": "test_product2 name",
    "product_description": "test_product2_description",
    "brand_id": "test_brand1",
}
USER_ENTITY = {
    "user_id": "test_user",
    "name": "test user name",
}
BRAND_ENTITY_1 = {
    "brand_id": "test_brand1",
    "name": "test brand1 name",
}
BRAND_ENTITY_2 = {
    "brand_id": "test_brand2",
    "name": "test brand2 name",
}

ONLINE_FEATURE_RESPNOSE = {
    "metadata": {
        "feature_names": [
            "IDENTIFIER",
            "test_batch_feature",
        ],
    },
    "results": [
        {
            "values": [
                "test_product1",
                "test_brand1",
                "test_product2",
                "test_brand2",
                "test query",
                "test_user",
            ],
            "statuses": ["PRESENT", "PRESENT"],
            "event_timestamps": ["1970-01-01T00:00:00Z", "1970-01-01T00:00:00Z"],
        },
        {
            "values": [
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            "statuses": ["PRESENT", "PRESENT"],
            "event_timestamps": ["1970-01-01T00:00:00Z", "1970-01-01T00:00:00Z"],
        },
    ],
}


@pytest_asyncio.fixture
async def mock_http_post(mocker):
    with aioresponses() as m:
        aiohttp_client.start()
        m.post(
            f"{settings.WYVERN_FEATURE_STORE_URL}{settings.WYVERN_ONLINE_FEATURES_PATH}",
            payload=ONLINE_FEATURE_RESPNOSE,
        )
        yield
        await aiohttp_client.stop()


@pytest.fixture
def mock_redis(mocker):
    with mocker.patch(
        "wyvern.redis.wyvern_redis.mget",
        side_effect=[
            [
                wyvern_encode(PRODUCT_ENTITY_1),
                wyvern_encode(PRODUCT_ENTITY_2),
                None,
                wyvern_encode(USER_ENTITY),
            ],
            [
                wyvern_encode(BRAND_ENTITY_1),
                wyvern_encode(BRAND_ENTITY_2),
            ],
        ],
    ):
        yield


@pytest.fixture
def mock_redis__duplicate_brand(mocker):
    with mocker.patch(
        "wyvern.redis.wyvern_redis.mget",
        side_effect=[
            [
                wyvern_encode(PRODUCT_ENTITY_1),
                wyvern_encode(PRODUCT_ENTITY_2__DUPLICATE_BRAND),
                None,
                wyvern_encode(USER_ENTITY),
            ],
            [
                wyvern_encode(BRAND_ENTITY_1),
                wyvern_encode(BRAND_ENTITY_1),
            ],
        ],
    ):
        yield


class Query(WyvernEntity):
    query: str

    def generate_identifier(self) -> Identifier:
        return Identifier(
            identifier=self.query,
            identifier_type="query",
        )


class User(WyvernEntity):
    user_id: str
    name: Optional[str]

    def generate_identifier(self) -> Identifier:
        return Identifier(
            identifier=self.user_id,
            identifier_type="user",
        )


class Brand(WyvernEntity):
    brand_id: str
    name: Optional[str]

    def generate_identifier(self) -> Identifier:
        return Identifier(
            identifier=self.brand_id,
            identifier_type="brand",
        )


class Product(ProductEntity):
    brand_id: Optional[str]
    brand: Optional[Brand]
    product_name: Optional[str]
    product_description: Optional[str]

    def nested_hydration(self) -> Dict[str, str]:
        """
        This method is used to hydrate nested entities.
        """
        return {
            "brand_id": "brand",
        }


class ProductSearchRankingRequest(
    BaseWyvernRequest,
    CandidateSetEntity[Product],
):
    query: Query
    candidates: List[Product]
    user: Optional[User]


class ProductSearchRankingResponse(BaseModel):
    """
    The response schema for the ProductSearchRanking pipeline
    """

    success: str


class RankingModelComponent(
    ModelComponent[
        ModelInput[Product, ProductSearchRankingRequest],
        ModelOutput[float],
    ],
):
    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        return {
            "RankingRealtimeFeatureComponent:f_1",
            "RankingRealtimeFeatureComponent:f_2",
            "RankingRealtimeFeatureComponent:f_3",
            "RankingRealtimeFeatureComponent:f_4",
            "test_feature_view:test_batch_feature",
        }

    async def inference(
        self,
        input: ModelInput[Product, ProductSearchRankingRequest],
        **kwargs,
    ) -> ModelOutput[float]:
        return ModelOutput(
            model_name="test_model",
            data={
                entity.identifier: hash(entity.identifier.identifier)
                for entity in input.entities
            },
        )


class RankingRealtimeFeatureComponent(
    RealtimeFeatureComponent[Product, Any, ProductSearchRankingRequest],
):
    def __init__(self):
        super().__init__(
            output_feature_names={
                "f_1",
                "f_2",
                "f_3",
                "f_4",
            },
        )

    async def compute_features(
        self,
        entity: Product,
        request: RealtimeFeatureRequest[ProductSearchRankingRequest],
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=entity.identifier,
            features={
                "f_1": 1.2,
                "f_2": 1.5,
                "f_3": "string_value",
                "f_4": [0, 1, 2, 3, 4, 5, 6, 7, 8],  # embedding
            },
        )


class RankingComponent(
    PipelineComponent[ProductSearchRankingRequest, ProductSearchRankingResponse],
):
    PATH = "/product-search-ranking"
    REQUEST_SCHEMA_CLASS = ProductSearchRankingRequest
    RESPONSE_SCHEMA_CLASS = ProductSearchRankingResponse

    def __init__(self) -> None:
        self.ranking_model_component = RankingModelComponent()
        super().__init__(self.ranking_model_component)

    async def execute(
        self,
        input: ProductSearchRankingRequest,
        **kwargs,
    ) -> ProductSearchRankingResponse:
        assert input.user and input.user.name == "test user name"
        assert input.candidates[0].product_name == "test_product1 name"
        assert input.candidates[0].product_description == "test_product1_description"
        assert input.candidates[0].brand_id == "test_brand1"
        assert input.candidates[0].brand is not None
        assert input.candidates[0].brand.brand_id == "test_brand1"
        assert input.candidates[0].brand.name == "test brand1 name"
        assert input.candidates[1].product_name == "test_product2 name"
        assert input.candidates[1].product_description == "test_product2_description"
        assert input.candidates[1].brand_id == "test_brand2"
        assert input.candidates[1].brand is not None
        assert input.candidates[1].brand.brand_id == "test_brand2"
        assert input.candidates[1].brand.name == "test brand2 name"

        # model inference
        model_output = await self.ranking_model_component.execute(
            input=ModelInput(
                request=input,
                entities=input.candidates,
            ),
        )
        assert model_output.model_name == "test_model"
        assert model_output.data[input.candidates[0].identifier] == float(
            hash(input.candidates[0].identifier.identifier),
        )
        assert model_output.data[input.candidates[1].identifier] == float(
            hash(input.candidates[1].identifier.identifier),
        )
        return ProductSearchRankingResponse(success="success")


@pytest.fixture
def test_client(mock_redis):
    wyvern_app = WyvernService.generate_app(
        route_components=[RankingComponent],
        realtime_feature_components=[],
    )
    yield TestClient(wyvern_app)


def test_get_all_identifiers():
    request = ProductSearchRankingRequest.parse_obj(
        {
            "request_id": "test_request_id",
            "query": {
                "query": "test query",
            },
            "candidates": [
                {
                    "product_id": "test_product1",
                },
                {
                    "product_id": "test_product2",
                },
            ],
            "user": {
                "user_id": "test_user",
            },
        },
    )

    assert set(request.get_all_identifiers()) == set(
        [
            Identifier(identifier="test_product1", identifier_type="product"),
            Identifier(identifier="test_product2", identifier_type="product"),
            Identifier(identifier="test query", identifier_type="query"),
            Identifier(identifier="test_user", identifier_type="user"),
        ],
    )


@pytest.mark.asyncio
async def test_hydrate(mock_redis):
    json_input = ProductSearchRankingRequest.parse_obj(
        {
            "request_id": "test_request_id",
            "query": {
                "query": "test query",
            },
            "candidates": [
                {
                    "product_id": "test_product1",
                },
                {
                    "product_id": "test_product2",
                },
            ],
            "user": {
                "user_id": "test_user",
            },
        },
    )
    # set up wyvern request context
    test_wyvern_request = WyvernRequest(
        method="GET",
        url="http://test.com",
        url_path="/",
        json=json_input,
        headers={},
        entity_store={},
        model_output_map={},
        events=[],
        feature_map=FeatureMap(feature_map={}),
    )
    request_context.set(test_wyvern_request)

    # mock redis mget

    # call component.hydrate
    component = RankingComponent()
    await component.hydrate(json_input)

    # assertion: all entities are hydrated correctly
    assert json_input.user and json_input.user.name == "test user name"
    assert json_input.candidates[0].product_name == "test_product1 name"
    assert json_input.candidates[0].product_description == "test_product1_description"
    assert json_input.candidates[0].brand_id == "test_brand1"
    assert json_input.candidates[0].brand is not None
    assert json_input.candidates[0].brand.brand_id == "test_brand1"
    assert json_input.candidates[0].brand.name == "test brand1 name"
    assert json_input.candidates[1].product_name == "test_product2 name"
    assert json_input.candidates[1].product_description == "test_product2_description"
    assert json_input.candidates[1].brand_id == "test_brand2"
    assert json_input.candidates[1].brand is not None
    assert json_input.candidates[1].brand.brand_id == "test_brand2"
    assert json_input.candidates[1].brand.name == "test brand2 name"
    all_entities = json_input.get_all_entities()
    assert len(all_entities) == 6

    # reset wyvern request context
    request_context.reset()


@pytest.mark.asyncio
async def test_hydrate__duplicate_brand(mock_redis__duplicate_brand):
    json_input = ProductSearchRankingRequest.parse_obj(
        {
            "request_id": "test_request_id",
            "query": {
                "query": "test query",
            },
            "candidates": [
                {
                    "product_id": "test_product1",
                },
                {
                    "product_id": "test_product2",
                },
            ],
            "user": {
                "user_id": "test_user",
            },
        },
    )
    # set up wyvern request context
    test_wyvern_request = WyvernRequest(
        method="GET",
        url="http://test.com",
        url_path="/",
        json=json_input,
        headers={},
        entity_store={},
        events=[],
        feature_map=FeatureMap(feature_map={}),
        model_output_map={},
    )
    request_context.set(test_wyvern_request)

    # mock redis mget

    # call component.hydrate
    component = RankingComponent()
    await component.hydrate(json_input)

    # assertion: all entities are hydrated correctly
    assert json_input.user and json_input.user.name == "test user name"
    assert json_input.candidates[0].product_name == "test_product1 name"
    assert json_input.candidates[0].product_description == "test_product1_description"
    assert json_input.candidates[0].brand_id == "test_brand1"
    assert json_input.candidates[0].brand is not None
    assert json_input.candidates[0].brand.brand_id == "test_brand1"
    assert json_input.candidates[0].brand.name == "test brand1 name"
    assert json_input.candidates[1].product_name == "test_product2 name"
    assert json_input.candidates[1].product_description == "test_product2_description"
    assert json_input.candidates[1].brand_id == "test_brand1"
    assert json_input.candidates[1].brand is not None
    assert json_input.candidates[1].brand.brand_id == "test_brand1"
    assert json_input.candidates[1].brand.name == "test brand1 name"
    all_entities = json_input.get_all_entities()
    assert len(all_entities) == 5

    # reset wyvern request context
    request_context.reset()


@pytest.mark.asyncio
async def test_end_to_end(mock_redis, mock_http_post, test_client):
    response = test_client.post(
        "/api/v1/product-search-ranking",
        json={
            "request_id": "test_request_id",
            "query": {
                "query": "test query",
            },
            "candidates": [
                {
                    "product_id": "test_product1",
                },
                {
                    "product_id": "test_product2",
                },
            ],
            "user": {
                "user_id": "test_user",
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {"success": "success"}
