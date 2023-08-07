# -*- coding: utf-8 -*-
import logging
from time import time
from typing import Any, Dict, List, Optional

import typer
from pydantic import BaseModel
from pyinstrument import Profiler

from wyvern.components.api_route_component import APIRouteComponent
from wyvern.components.features.feature_retrieval_pipeline import (
    FeatureRetrievalPipeline,
    FeatureRetrievalPipelineRequest,
)
from wyvern.components.features.realtime_features_component import (
    RealtimeFeatureComponent,
    RealtimeFeatureRequest,
)
from wyvern.entities.candidate_entities import CandidateSetEntity
from wyvern.entities.feature_entities import FeatureData
from wyvern.entities.identifier import (
    CompositeIdentifier,
    Identifier,
    SimpleIdentifierType,
)
from wyvern.entities.identifier_entities import ProductEntity, QueryEntity, UserEntity
from wyvern.entities.request import BaseWyvernRequest
from wyvern.service import WyvernService
from wyvern.wyvern_typing import WyvernFeature

wyvern_cli_app = typer.Typer()

logger = logging.getLogger(__name__)


class Product(ProductEntity):
    product_id: str
    opensearch_score: Optional[float]
    candidate_order: Optional[int]
    matched_queries: List[str] = []


class Query(QueryEntity):
    query: str


class User(UserEntity):
    user_id: str
    user_name: str


class FeatureStoreRequest(
    BaseWyvernRequest,
    CandidateSetEntity[Product],
):
    request_id: str
    query: Query
    candidates: List[Product]
    user: Optional[User]


class FeatureStoreResponse(BaseModel):
    feature_data: Dict[str, FeatureData]


class RealTimeProductFeature(RealtimeFeatureComponent[Product, Any, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={"f_opensearch_score"},
        )

    async def compute_features(
        self,
        entity: Product,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=entity.identifier,
            features={
                "f_opensearch_score": entity.opensearch_score,
            },
        )


class RealTimeMatchedQueriesProductFeature(
    RealtimeFeatureComponent[Product, Query, Any],
):
    def __init__(self):
        super().__init__(
            output_feature_names=set(),
        )

    async def compute_composite_features(
        self,
        primary_entity: Product,
        secondary_entity: Query,
        request: Any,
    ) -> Optional[FeatureData]:
        features: Dict[str, WyvernFeature] = {
            f"f_matched_queries_{query}": 1.0
            for query in primary_entity.matched_queries
        }

        return FeatureData(
            identifier=CompositeIdentifier(
                primary_entity.identifier,
                secondary_entity.identifier,
            ),
            features=features,
        )


class RealTimeNumberOfCandidatesFeature(
    RealtimeFeatureComponent[Any, Any, FeatureStoreRequest],
):
    def __init__(self):
        super().__init__(
            output_feature_names={"f_number_of_candidates"},
        )

    async def compute_request_features(
        self,
        request: RealtimeFeatureRequest[FeatureStoreRequest],
    ) -> Optional[FeatureData]:

        return FeatureData(
            identifier=Identifier(
                identifier=request.request.request_id,
                identifier_type=SimpleIdentifierType.REQUEST,
            ),
            features={
                "f_number_of_candidates": len(request.request.candidates),
            },
        )


class RealTimeQueryFeature(RealtimeFeatureComponent[Query, Any, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={"f_query_length"},
        )

    async def compute_features(
        self,
        entity: Query,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=entity.identifier,
            features={
                "f_query_length": len(entity.query),
            },
        )


class RealTimeStringFeature(RealtimeFeatureComponent[Query, Any, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={"f_query"},
        )

    async def compute_features(
        self,
        entity: Query,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=entity.identifier,
            features={
                "f_query": entity.query,
            },
        )


class RealTimeEmbeddingFeature(RealtimeFeatureComponent[Query, Any, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={"f_query_embedding_vector_8"},
        )

    async def compute_features(
        self,
        entity: Query,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=entity.identifier,
            features={"f_query_embedding_vector_8": [1, 2, 3, 4, 5, 6, 7, 8]},
        )


class RealTimeQueryProductFeature(RealtimeFeatureComponent[Product, Query, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={
                "f_query_product_name_edit_distance",
                "f_query_product_name_jaccard_similarity",
            },
        )

    async def compute_composite_features(
        self,
        primary_entity: Product,
        secondary_entity: Query,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=CompositeIdentifier(
                primary_identifier=primary_entity.identifier,
                secondary_identifier=secondary_entity.identifier,
            ),
            features={
                "f_query_product_name_edit_distance": len(secondary_entity.query)
                - len(primary_entity.product_id),
                "f_query_product_name_jaccard_similarity": len(
                    primary_entity.product_id,
                )
                - len(secondary_entity.query),
            },
        )


class RealTimeUserFeature(RealtimeFeatureComponent[User, Any, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={"f_user_name_length"},
        )

    async def compute_features(
        self,
        entity: User,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=entity.identifier,
            features={
                "f_user_name_length": len(entity.user_name),
            },
        )


class RealTimeUserProductFeature(RealtimeFeatureComponent[Product, User, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={
                "f_user_product_name_edit_distance",
                "f_user_product_name_jaccard_similarity",
            },
        )

    async def compute_composite_features(
        self,
        primary_entity: Product,
        secondary_entity: User,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=CompositeIdentifier(
                primary_identifier=primary_entity.identifier,
                secondary_identifier=secondary_entity.identifier,
            ),
            features={
                "f_user_product_name_edit_distance": len(secondary_entity.user_name)
                - len(primary_entity.product_id),
                "f_user_product_name_jaccard_similarity": len(primary_entity.product_id)
                - len(secondary_entity.user_name),
            },
        )


class RealTimeUserQueryFeature(RealtimeFeatureComponent[Query, User, Any]):
    def __init__(self):
        super().__init__(
            output_feature_names={
                "f_user_query_name_edit_distance",
                "f_user_query_name_jaccard_similarity",
            },
        )

    async def compute_composite_features(
        self,
        primary_entity: Query,
        secondary_entity: User,
        request: Any,
    ) -> Optional[FeatureData]:
        return FeatureData(
            identifier=CompositeIdentifier(
                primary_identifier=primary_entity.identifier,
                secondary_identifier=secondary_entity.identifier,
            ),
            features={
                "f_user_query_name_edit_distance": len(secondary_entity.user_name)
                - len(primary_entity.query),
                "f_user_query_name_jaccard_similarity": len(primary_entity.query)
                - len(secondary_entity.user_name),
            },
        )


class RealTimeFeatureTestingComponent(
    APIRouteComponent[FeatureStoreRequest, FeatureStoreResponse],
):
    PATH = "/real-time-features-testing"
    REQUEST_SCHEMA_CLASS = FeatureStoreRequest
    RESPONSE_SCHEMA_CLASS = FeatureStoreResponse

    def __init__(self):
        self.feature_retrieval_pipeline = FeatureRetrievalPipeline(
            name="real-time-features-testing",
        )
        super().__init__(self.feature_retrieval_pipeline)

    async def execute(
        self, input: FeatureStoreRequest, **kwargs
    ) -> FeatureStoreResponse:
        profiler = Profiler()
        profiler.start()

        # TODO (suchintan) -- actually request some features here
        request = FeatureRetrievalPipelineRequest[FeatureStoreRequest](
            request=input,
            requested_feature_names={
                "RealTimeProductFeature:f_opensearch_score",
                "RealTimeNumberOfCandidatesFeature:f_number_of_candidates",
                "RealTimeQueryFeature:f_query_length",
                "RealTimeQueryProductFeature:f_query_product_name_edit_distance",
                "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity",
                "RealTimeUserFeature:f_user_name_length",
                "RealTimeUserProductFeature:f_user_product_name_edit_distance",
                "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity",
                "RealTimeUserQueryFeature:f_user_query_name_edit_distance",
                "RealTimeUserQueryFeature:f_user_query_name_jaccard_similarity",
                "RealTimeStringFeature:f_query",
                "RealTimeEmbeddingFeature:f_query_embedding_vector_8",
            },
            feature_overrides={RealTimeMatchedQueriesProductFeature},
        )

        time_start = time()
        feature_map = await self.feature_retrieval_pipeline.execute(request)
        logger.info(f"operation feature_retrieval took:{time()-time_start:2.4f} sec")
        profiler.stop()
        profiler.print()
        return FeatureStoreResponse(
            feature_data={
                str(identifier): feature_map.feature_map[identifier]
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
        route_components=[RealTimeFeatureTestingComponent],
        host=host,
        port=port,
    )


if __name__ == "__main__":
    wyvern_cli_app()
