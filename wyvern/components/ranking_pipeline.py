# -*- coding: utf-8 -*-
from typing import Any, Generic, List, Optional

from pydantic import BaseModel

from wyvern.components.business_logic.business_logic import (
    BusinessLogicPipeline,
    BusinessLogicRequest,
)
from wyvern.components.candidates.candidate_logger import (
    CandidateEventLoggingComponent,
    CandidateEventLoggingRequest,
)
from wyvern.components.events.events import LoggedEvent
from wyvern.components.impressions.impression_logger import (
    ImpressionEventLoggingComponent,
    ImpressionEventLoggingRequest,
)
from wyvern.components.models.model_component import ModelComponent
from wyvern.components.pagination.pagination_component import (
    PaginationComponent,
    PaginationRequest,
)
from wyvern.components.pagination.pagination_fields import PaginationFields
from wyvern.components.pipeline_component import PipelineComponent
from wyvern.entities.candidate_entities import ScoredCandidate
from wyvern.entities.identifier_entities import QueryEntity
from wyvern.entities.model_entities import ModelInput
from wyvern.entities.request import BaseWyvernRequest
from wyvern.event_logging import event_logger
from wyvern.wyvern_typing import WYVERN_ENTITY


class RankingRequest(
    BaseWyvernRequest,
    PaginationFields,
    Generic[WYVERN_ENTITY],
):
    """
    This is the request for the ranking pipeline.

    Attributes:
        query: the query entity
        entities: the list of entities to rank
    """

    query: QueryEntity
    entities: List[WYVERN_ENTITY]


class ResponseEntity(BaseModel):
    """
    This is the response entity.

    Attributes:
        entity_id: the identifier of the entity
        ranked_score: the ranked score of the entity
    """

    entity_id: str
    ranked_score: float


class RankingResponse(BaseModel):
    """
    This is the response for the ranking pipeline.

    Attributes:
        ranked_entities: the list of ranked entities
        events: the list of logged events
    """

    ranked_entities: List[ResponseEntity]
    events: Optional[List[LoggedEvent[Any]]]


class RankingPipeline(
    PipelineComponent[RankingRequest, RankingResponse],
    Generic[WYVERN_ENTITY],
):
    """
    This is the ranking pipeline.

    Attributes:
        PATH: the path of the API. This is used in the API routing. The default value is "/ranking".
    """

    PATH: str = "/ranking"

    def __init__(self, name: Optional[str] = None):
        self.pagination_component = PaginationComponent[
            ScoredCandidate[WYVERN_ENTITY]
        ]()
        self.ranking_model = self.get_model()
        self.candidate_logging_component = CandidateEventLoggingComponent[
            WYVERN_ENTITY,
            RankingRequest[WYVERN_ENTITY],
        ]()
        self.impression_logging_component = ImpressionEventLoggingComponent[
            WYVERN_ENTITY,
            RankingRequest[WYVERN_ENTITY],
        ]()

        upstream_components = [
            self.pagination_component,
            self.ranking_model,
            self.candidate_logging_component,
            self.impression_logging_component,
        ]
        self.business_logic_pipeline: BusinessLogicPipeline
        business_logic = self.get_business_logic()
        if business_logic:
            self.business_logic_pipeline = business_logic
        else:
            self.business_logic_pipeline = BusinessLogicPipeline[
                WYVERN_ENTITY,
                RankingRequest[WYVERN_ENTITY],
            ]()
        upstream_components.append(self.business_logic_pipeline)

        super().__init__(
            *upstream_components,
            name=name,
        )

    def get_model(self) -> ModelComponent:
        """
        This is the ranking model.

        The model input should be a subclass of ModelInput.
        Its output should be scored entities
        """
        raise NotImplementedError

    def get_business_logic(self) -> Optional[BusinessLogicPipeline]:
        """
        This is the business logic pipeline. It is optional. If not provided, the ranking pipeline will not
        apply any business logic.

        The business logic pipeline should be a subclass of BusinessLogicPipeline. Some examples of business logic
        for ranking pipeline are:
        1. Deduplication
        2. Filtering
        3. (De)boosting
        """
        return None

    async def execute(
        self,
        input: RankingRequest[WYVERN_ENTITY],
        **kwargs,
    ) -> RankingResponse:
        entities: List[ScoredCandidate] = [
            ScoredCandidate(
                entity=entity,
                score=i,
            )
            for i, entity in enumerate(input.entities)
        ]
        candidate_logging_request = CandidateEventLoggingRequest[
            WYVERN_ENTITY,
            RankingRequest[WYVERN_ENTITY],
        ](
            request=input,
            scored_candidates=entities,
        )
        await self.candidate_logging_component.execute(candidate_logging_request)

        if not self.bypass_ranking(input):
            entities = await self.rank_entities(input)

        pagination_request = PaginationRequest[ScoredCandidate[WYVERN_ENTITY]](
            pagination_fields=input,
            entities=entities,
        )
        paginated_candidates = await self.pagination_component.execute(
            pagination_request,
        )

        impression_logging_request = ImpressionEventLoggingRequest[
            WYVERN_ENTITY,
            RankingRequest[WYVERN_ENTITY],
        ](
            scored_impressions=paginated_candidates,
            request=input,
        )
        await self.impression_logging_component.execute(impression_logging_request)

        response_ranked_entities = [
            ResponseEntity(
                entity_id=candidate.entity.identifier.identifier,
                ranked_score=candidate.score,
            )
            for candidate in paginated_candidates
        ]

        response = RankingResponse(
            ranked_entities=response_ranked_entities,
            events=event_logger.get_logged_events() if input.include_events else None,
        )

        return response

    async def rank_entities(
        self,
        request: RankingRequest[WYVERN_ENTITY],
    ) -> List[ScoredCandidate[WYVERN_ENTITY]]:
        """
        This function ranks the entities.

        1. It first calls the ranking model to get the model scores for the entities.
        2. It then calls the business logic pipeline to adjust the model scores.
        3. It returns the entities with adjusted rank score.

        Args:
            request: the ranking request

        Returns:
            A list of ScoredCandidate
        """
        model_input = ModelInput[WYVERN_ENTITY, RankingRequest[WYVERN_ENTITY]](
            request=request,
            entities=request.entities,
        )
        model_outputs = await self.ranking_model.execute(model_input)

        scored_candidates: List[ScoredCandidate] = [
            ScoredCandidate(
                entity=candidate,
                score=(
                    model_outputs.data.get(candidate.identifier) or 0
                ),  # TODO (shu): what to do if model score is None?
            )
            for i, candidate in enumerate(request.entities)
        ]

        business_logic_request = BusinessLogicRequest[
            WYVERN_ENTITY,
            RankingRequest[WYVERN_ENTITY],
        ](
            request=request,
            scored_candidates=scored_candidates,
        )

        # business_logic makes sure the candidates are sorted
        business_logic_response = await self.business_logic_pipeline.execute(
            business_logic_request,
        )
        return business_logic_response.adjusted_candidates

    def bypass_ranking(self, request: RankingRequest[WYVERN_ENTITY]) -> bool:
        return False
