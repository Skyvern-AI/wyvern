# -*- coding: utf-8 -*-
from typing import Dict, List

import pytest

from wyvern import request_context
from wyvern.components.business_logic.business_logic import (
    BusinessLogicPipeline,
    BusinessLogicRequest,
    BusinessLogicResponse,
)
from wyvern.components.business_logic.pinning_business_logic import (
    PinningBusinessLogicComponent,
)
from wyvern.entities.candidate_entities import ScoredCandidate
from wyvern.entities.feature_entities import FeatureMap
from wyvern.entities.identifier_entities import ProductEntity
from wyvern.entities.request import BaseWyvernRequest
from wyvern.wyvern_request import WyvernRequest


async def set_up_pinning_components(
    scored_candidates: List[ScoredCandidate[ProductEntity]],
    entity_pins: Dict[str, int],
    allow_down_ranking=True,
) -> BusinessLogicResponse[ProductEntity, BaseWyvernRequest]:
    class TestPins(PinningBusinessLogicComponent[ProductEntity, BaseWyvernRequest]):
        async def execute(
            self,
            input: BusinessLogicRequest[ProductEntity, BaseWyvernRequest],
            **kwargs,
        ) -> List[ScoredCandidate[ProductEntity]]:
            return self.pin(
                input.scored_candidates,
                entity_pins=entity_pins,
                allow_down_ranking=allow_down_ranking,
            )

    class TestBusinessLogicPipeline(
        BusinessLogicPipeline[ProductEntity, BaseWyvernRequest],
    ):
        def __init__(self):
            """
            Add new business logic components here. All business logic steps are executed in the order defined here.
            """
            super().__init__(
                TestPins(),
                name="test_business_logic_pipeline",
            )

    pipeline = TestBusinessLogicPipeline()
    await pipeline.initialize()

    request = BusinessLogicRequest[ProductEntity, BaseWyvernRequest](
        request=BaseWyvernRequest(request_id="123"),
        scored_candidates=scored_candidates,
    )

    request_context.set(
        WyvernRequest(
            method="POST",
            url="TestTest",
            url_path="Test",
            json=request,
            headers={},
            entity_store={},
            events=[],
            feature_map=FeatureMap(feature_map={}),
        ),
    )
    return await pipeline.execute(request)


def generate_scored_candidates(id_score_pairs: Dict[str, float]):
    return [
        ScoredCandidate(entity=ProductEntity(product_id=id), score=score)
        for id, score in id_score_pairs.items()
    ]


@pytest.mark.asyncio
async def test_pins():
    scored_candidates = generate_scored_candidates(
        {
            "product_1": 6,
            "product_2": 5,
            "product_3": 4,
            "product_4": 3,
            "product_5": 2,
            "product_6": 1,
        },
    )

    pins = {
        "product_6": 11,
        "product_5": 10,
        "product_3": 0,
        "product_2": 0,
        "product_4": 2,
    }

    result = await set_up_pinning_components(scored_candidates, pins)

    adjusted_candidates = [
        candidate.entity.product_id for candidate in result.adjusted_candidates
    ]
    # Bug -- product_4 is coming in at index 3, not index 2 like requested.. due to the other boosts
    expected_order = [
        "product_2",
        "product_3",
        "product_1",
        "product_4",
        "product_5",
        "product_6",
    ]
    assert adjusted_candidates == expected_order


@pytest.mark.asyncio
async def test_pins__no_down_ranking():
    scored_candidates = generate_scored_candidates(
        {
            "product_1": 6,
            "product_2": 5,
            "product_3": 4,
            "product_4": 3,
            "product_5": 2,
            "product_6": 1,
        },
    )

    pins = {
        "product_6": 11,
        "product_5": 12,
        "product_3": 0,
        "product_2": 22,
        "product_4": 2,
    }

    result = await set_up_pinning_components(
        scored_candidates,
        pins,
        allow_down_ranking=False,
    )

    adjusted_candidates = [
        candidate.entity.product_id for candidate in result.adjusted_candidates
    ]
    # Bug -- product_4 is coming in at index 3, not index 2 like requested.. due to the other boosts
    expected_order = [
        "product_3",
        "product_1",
        "product_2",
        "product_4",
        "product_5",
        "product_6",
    ]
    assert adjusted_candidates == expected_order


"""
TODO (suchintan):
Test cases:
1. Pin any product
2. Pin multiple products in different order
3. Allow down ranking = false and true
4. Pin a product that is not in the list
5. Pin a product that is in the list but not in the top 10
6. Pin multiple products to the same position
7. Pin to the top of the list
8. Pin to the bottom of the list
"""
