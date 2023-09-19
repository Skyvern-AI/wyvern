# -*- coding: utf-8 -*-
from typing import List

import pytest
from fastapi.testclient import TestClient

from wyvern.components.business_logic.business_logic import (
    SingleEntityBusinessLogicComponent,
    SingleEntityBusinessLogicPipeline,
    SingleEntityBusinessLogicRequest,
)
from wyvern.components.models.model_chain_component import SingleEntityModelChain
from wyvern.components.models.model_component import SingleEntityModelComponent
from wyvern.components.single_entity_pipeline import (
    SingleEntityPipeline,
    SingleEntityPipelineResponse,
)
from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import WyvernEntity
from wyvern.entities.model_entities import ModelOutput
from wyvern.entities.request import BaseWyvernRequest
from wyvern.service import WyvernService


class Seller(WyvernEntity):
    seller_id: str

    def generate_identifier(self) -> Identifier:
        return Identifier(
            identifier=self.seller_id,
            identifier_type="seller",
        )


class Buyer(WyvernEntity):
    buyer_id: str

    def generate_identifier(self) -> Identifier:
        return Identifier(
            identifier=self.buyer_id,
            identifier_type="buyer",
        )


class Order(WyvernEntity):
    order_id: str

    def generate_identifier(self) -> Identifier:
        return Identifier(
            identifier=self.order_id,
            identifier_type="order",
        )


class FraudRequest(BaseWyvernRequest):
    seller: Seller
    buyer: Buyer
    order: Order


class FraudResponse(SingleEntityPipelineResponse[float]):
    reasons: List[str]


class FraudRuleModel(SingleEntityModelComponent[FraudRequest, ModelOutput[float]]):
    async def inference(self, input: FraudRequest, **kwargs) -> ModelOutput[float]:
        return ModelOutput(
            data={
                input.order.identifier: 1,
            },
        )


class FraudAssessmentModel(
    SingleEntityModelComponent[FraudRequest, ModelOutput[float]],
):
    async def inference(self, input: FraudRequest, **kwargs) -> ModelOutput[float]:
        return ModelOutput(
            data={
                input.order.identifier: 1,
            },
        )


fraud_model = SingleEntityModelChain[FraudRequest, ModelOutput[float]](
    FraudRuleModel(),
    FraudAssessmentModel(),
    name="fraud_model",
)


class FraudBusinessLogicComponent(
    SingleEntityBusinessLogicComponent[FraudRequest, float],
):
    async def execute(
        self,
        input: SingleEntityBusinessLogicRequest[FraudRequest, float],
        **kwargs,
    ) -> float:
        if input.request.seller.identifier.identifier == "test_seller_new":
            return 0.0
        return input.model_output


fraud_biz_pipeline = SingleEntityBusinessLogicPipeline(
    FraudBusinessLogicComponent(),
    name="fraud_biz_pipeline",
)


class FraudPipeline(SingleEntityPipeline[FraudRequest, float]):
    PATH = "/fraud"
    REQUEST_SCHEMA_CLASS = FraudRequest
    RESPONSE_SCHEMA_CLASS = FraudResponse

    def generate_response(
        self,
        input: FraudRequest,
        pipeline_output: float,
    ) -> FraudResponse:
        if pipeline_output == 0.0:
            return FraudResponse(
                data=pipeline_output,
                reasons=["Fraudulent order detected!"],
            )
        return FraudResponse(
            data=pipeline_output,
            reasons=[],
        )


fraud_pipeline = FraudPipeline(model=fraud_model, business_logic=fraud_biz_pipeline)


@pytest.fixture
def mock_redis(mocker):
    with mocker.patch(
        "wyvern.redis.wyvern_redis.mget",
        return_value=[],
    ):
        yield


@pytest.fixture
def test_client(mock_redis):
    wyvern_app = WyvernService.generate_app(
        route_components=[fraud_pipeline],
    )
    yield TestClient(wyvern_app)


def test_end_to_end(test_client):
    response = test_client.post(
        "/api/v1/fraud",
        json={
            "request_id": "test_request_id",
            "seller": {"seller_id": "test_seller_id"},
            "buyer": {"buyer_id": "test_buyer_id"},
            "order": {"order_id": "test_order_id"},
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": 1.0, "reasons": []}


def test_end_to_end__new_seller(test_client):
    response = test_client.post(
        "/api/v1/fraud",
        json={
            "request_id": "test_request_id",
            "seller": {"seller_id": "test_seller_new"},
            "buyer": {"buyer_id": "test_buyer_id"},
            "order": {"order_id": "test_order_id"},
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": 0.0, "reasons": ["Fraudulent order detected!"]}
