# -*- coding: utf-8 -*-
from typing import Any, Generic, List, Optional, Type

from pydantic import BaseModel
from pydantic.generics import GenericModel

from wyvern.components.business_logic.business_logic import (
    BusinessLogicPipeline,
    BusinessLogicRequest,
)
from wyvern.components.candidates.candidate_logger import CandidateEventLoggingComponent
from wyvern.components.events.events import LoggedEvent
from wyvern.components.impressions.impression_logger import (
    ImpressionEventLoggingComponent,
    ImpressionEventLoggingRequest,
)
from wyvern.components.models.model_component import ModelComponent, ModelInput
from wyvern.components.pagination.pagination_component import (
    PaginationComponent,
    PaginationRequest,
)
from wyvern.components.pagination.pagination_fields import PaginationFields
from wyvern.components.pipeline_component import PipelineComponent
from wyvern.entities.candidate_entities import ScoredCandidate
from wyvern.entities.identifier_entities import QueryEntity
from wyvern.entities.request import BaseWyvernRequest
from wyvern.event_logging import event_logger
from wyvern.wyvern_typing import PRODUCT_ENTITY


class ProductRankingRequest(
    BaseWyvernRequest,
    PaginationFields,
    Generic[PRODUCT_ENTITY],
):
    request_id: str
    query: QueryEntity
    candidates: List[PRODUCT_ENTITY]


class ResponseProduct(BaseModel):
    product_id: str
    ranked_score: float


class ProductRankingResponse(GenericModel, Generic[PRODUCT_ENTITY]):
    ranked_products: List[ResponseProduct]
    events: Optional[List[LoggedEvent[Any]]]


class ProductRankingPipeline(
    PipelineComponent[ProductRankingRequest, ProductRankingResponse],
    Generic[PRODUCT_ENTITY],
):
    PATH: str = "/product-ranking"

    def __init__(self, name: Optional[str] = None):
        self.pagination_component = PaginationComponent[
            ScoredCandidate[PRODUCT_ENTITY]
        ]()
        self.ranking_model = self.model()
        self.candidate_logging_component = CandidateEventLoggingComponent[
            PRODUCT_ENTITY,
            ProductRankingRequest[PRODUCT_ENTITY],
        ]()
        self.impression_logging_component = ImpressionEventLoggingComponent[
            PRODUCT_ENTITY,
            ProductRankingRequest[PRODUCT_ENTITY],
        ]()
        upstream_components = [
            self.pagination_component,
            self.ranking_model,
            self.candidate_logging_component,
            self.impression_logging_component,
        ]
        self.business_logic_pipeline: Optional[BusinessLogicPipeline] = None
        if self.business_logic:
            self.business_logic_pipeline = self.business_logic()
            upstream_components.append(self.business_logic_pipeline)

        super().__init__(
            *upstream_components,
            name=name,
        )

    @property
    def model(self) -> Type[ModelComponent]:
        """
        The model component input type should be a subclass of ModelInput.
        Its output type should be scored candidates
        """
        raise NotImplementedError

    @property
    def business_logic(self) -> Optional[Type[BusinessLogicPipeline]]:
        return None

    async def execute(
        self,
        input: ProductRankingRequest[PRODUCT_ENTITY],
        **kwargs,
    ) -> ProductRankingResponse[PRODUCT_ENTITY]:
        ranked_candidates = await self.rank_products(input)

        pagination_request = PaginationRequest[ScoredCandidate[PRODUCT_ENTITY]](
            pagination_fields=input,
            entities=ranked_candidates,
        )
        paginated_candidates = await self.pagination_component.execute(
            pagination_request,
        )

        # TODO (suchintan): This should be automatic  -- add this to the pipeline abstraction
        impression_logging_request = ImpressionEventLoggingRequest[
            PRODUCT_ENTITY,
            ProductRankingRequest[PRODUCT_ENTITY],
        ](
            scored_impressions=paginated_candidates,
            request=input,
        )
        await self.impression_logging_component.execute(impression_logging_request)

        ranked_products = [
            ResponseProduct(
                product_id=candidate.entity.product_id,
                ranked_score=candidate.score,
            )
            for candidate in paginated_candidates
        ]

        response = ProductRankingResponse[PRODUCT_ENTITY](
            ranked_products=ranked_products,
            events=event_logger.get_logged_events() if input.include_events else None,
        )

        return response

    async def rank_products(
        self,
        request: ProductRankingRequest[PRODUCT_ENTITY],
    ) -> List[ScoredCandidate[PRODUCT_ENTITY]]:
        model_input = ModelInput[PRODUCT_ENTITY, ProductRankingRequest[PRODUCT_ENTITY]](
            request=request,
            entities=request.candidates,
        )
        model_outputs = await self.ranking_model.execute(model_input)

        # does the scored_candidates need to be sorted?
        scored_candidates: List[ScoredCandidate] = [
            ScoredCandidate(
                entity=candidate,
                score=(
                    model_outputs.get(candidate.product_id) or 0
                ),  # TODO (shu): what to do if model score is None?
            )
            for i, candidate in enumerate(request.candidates)
        ]

        if self.business_logic_pipeline:
            business_logic_request = BusinessLogicRequest[
                PRODUCT_ENTITY,
                ProductRankingRequest[PRODUCT_ENTITY],
            ](
                request=request,
                scored_candidates=scored_candidates,
            )

            business_logic_response = await self.business_logic_pipeline.execute(
                business_logic_request,
            )
            return business_logic_response.adjusted_candidates
        return scored_candidates
