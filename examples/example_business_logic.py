# -*- coding: utf-8 -*-
import asyncio
import json
import logging
from typing import List

from pydantic import BaseModel

from wyvern.components.business_logic.boosting_business_logic import (
    BoostingBusinessLogicComponent,
)
from wyvern.components.business_logic.business_logic import (
    BusinessLogicEvent,
    BusinessLogicPipeline,
    BusinessLogicRequest,
)
from wyvern.components.component import Component
from wyvern.entities.candidate_entities import CandidateSetEntity, ScoredCandidate
from wyvern.entities.identifier_entities import ProductEntity, QueryEntity
from wyvern.entities.request import BaseWyvernRequest

logger = logging.getLogger(__name__)


class SimpleProductEntity(ProductEntity):
    product_name: str = ""
    product_description: str = ""


class ExampleProductSearchRankingRequest(
    BaseWyvernRequest,
    QueryEntity,
    CandidateSetEntity[SimpleProductEntity],
):
    pass


class CandleBoostingBusinessLogicComponent(
    BoostingBusinessLogicComponent[
        SimpleProductEntity,
        ExampleProductSearchRankingRequest,
    ],
):
    async def execute(
        self,
        input: BusinessLogicRequest[
            SimpleProductEntity,
            ExampleProductSearchRankingRequest,
        ],
        **kwargs,
    ) -> List[ScoredCandidate[SimpleProductEntity]]:
        # TODO (suchintan): Feature request: Add a way to load a CSV from S3
        # Define this in a CSV (query, entity_keys, boost)
        # Get access to S3
        # Load CSV from S3
        # Reference the file and boost it -- reload the file every 15 minutes or something like that
        logger.info(f"Boosting candles for query={input.request.query}")
        if input.request.query == "candle":
            return self.boost(input.scored_candidates, entity_keys={"3"}, boost=100)
        else:
            return input.scored_candidates


class AlwaysBoostWaxSealProduct(
    BoostingBusinessLogicComponent[
        SimpleProductEntity,
        ExampleProductSearchRankingRequest,
    ],
):
    async def execute(
        self,
        input: BusinessLogicRequest[
            SimpleProductEntity,
            ExampleProductSearchRankingRequest,
        ],
        **kwargs,
    ) -> List[ScoredCandidate[SimpleProductEntity]]:
        return self.boost(input.scored_candidates, entity_keys={"7"}, boost=100)


class SearchBusinessLogicPipeline(
    BusinessLogicPipeline[SimpleProductEntity, ExampleProductSearchRankingRequest],
):
    def __init__(self):
        super().__init__(
            CandleBoostingBusinessLogicComponent(),
            AlwaysBoostWaxSealProduct(),
            name="search_business_logic_pipeline",
        )


search_business_logic_pipeline = SearchBusinessLogicPipeline()


class ExampleProductSearchRankingCandidateResponse(BaseModel):
    product_name: str
    old_rank: int
    old_score: float
    new_rank: int
    new_score: float


class ExampleProductSearchRankingResponse(BaseModel):
    ranked_products: List[ExampleProductSearchRankingCandidateResponse]
    events: List[BusinessLogicEvent]


class ProductQueryRankingBusinessLogicComponent(
    Component[ExampleProductSearchRankingRequest, ExampleProductSearchRankingResponse],
):
    def __init__(self):
        super().__init__(
            search_business_logic_pipeline,
            name="product_query_ranking_business_logic_component",
        )

    async def execute(
        self, input: ExampleProductSearchRankingRequest, **kwargs
    ) -> ExampleProductSearchRankingResponse:
        logger.info(f"Input request: {input}")
        # Set up a really silly score
        scored_candidates: List[ScoredCandidate] = [
            ScoredCandidate(entity=candidate, score=(len(input.candidates) - i))
            for i, candidate in enumerate(input.candidates)
        ]

        business_logic_request = BusinessLogicRequest[
            SimpleProductEntity,
            ExampleProductSearchRankingRequest,
        ](
            request=input,
            scored_candidates=scored_candidates,
        )

        ranked_products = await search_business_logic_pipeline.execute(
            business_logic_request,
        )

        pretty_ranked_products = [
            ExampleProductSearchRankingCandidateResponse(
                product_name=entity_score.entity.product_name,
                old_rank=input.candidates.index(entity_score.entity),
                old_score=ranked_products.request.scored_candidates[
                    input.candidates.index(entity_score.entity)
                ].score,
                new_rank=i,
                new_score=entity_score.score,
            )
            for i, entity_score in enumerate(ranked_products.adjusted_candidates)
        ]

        return ExampleProductSearchRankingResponse(
            ranked_products=pretty_ranked_products,
        )


def create_example_business_logic_component() -> ProductQueryRankingBusinessLogicComponent:
    business_logic_component = ProductQueryRankingBusinessLogicComponent()
    return business_logic_component


async def sample_product_query_ranking_request() -> None:
    """
    How to run this: `python wyvern/examples/example_business_logic.py`

    Json representation of the request:
    {
        "request_id": "rrr",
        "query": "candle",
        "candidates": [
            {"product_id": "1", "product_name": "scented candle"},
            {"product_id": "2", "product_name": "hot candle"},
            {"product_id": "3", "product_name": "pumpkin candle"},
            {"product_id": "4", "product_name": "unrelated item"},
            {"product_id": "5", "product_name": "candle holder accessory"},
            {"product_id": "6", "product_name": "earwax holder"},
            {"product_id": "7", "product_name": "wax seal"}
       ],
    }
    """
    logger.info("Start query product business logic case...")
    req = ExampleProductSearchRankingRequest(
        request_id="rrr",
        query="candle",
        candidates=[
            SimpleProductEntity(product_id="1", product_name="scented candle"),
            SimpleProductEntity(product_id="2", product_name="hot candle"),
            SimpleProductEntity(product_id="3", product_name="pumpkin candle"),
            SimpleProductEntity(product_id="4", product_name="unrelated item"),
            SimpleProductEntity(product_id="5", product_name="candle holder accessory"),
            SimpleProductEntity(product_id="6", product_name="earwax holder"),
            SimpleProductEntity(product_id="7", product_name="wax seal"),
        ],
    )

    component = create_example_business_logic_component()
    await component.initialize()

    response = await component.execute(req)

    json_formatted_str = json.dumps(
        response.dict(),
        indent=2,
    )
    logger.info(f"Response: {json_formatted_str}")


if __name__ == "__main__":
    asyncio.run(sample_product_query_ranking_request())
