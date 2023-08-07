# -*- coding: utf-8 -*-
import pytest
from starlette.testclient import TestClient

from examples.real_time_features_main import *  # noqa: F401, F403
from examples.real_time_features_main import RealTimeFeatureTestingComponent
from tests.scenarios.test_product_ranking import (  # noqa: F401
    RankingRealtimeFeatureComponent,
)
from wyvern.components.features.feature_store import feature_store_retrieval_component
from wyvern.entities.feature_entities import FeatureMap
from wyvern.feature_store.historical_feature_util import separate_real_time_features
from wyvern.service import WyvernService


@pytest.fixture
def mock_redis(mocker):
    """
    Mocks the redis call. Each entry under `return_value` corresponds to a single entity fetch from Redis
    """
    with mocker.patch(
        "wyvern.redis.wyvern_redis.mget",
        return_value=[None, None, None, None, None],
    ):
        yield


@pytest.fixture
def mock_feature_store(mocker):
    with mocker.patch.object(
        feature_store_retrieval_component,
        "fetch_features_from_feature_store",
        return_value=FeatureMap(feature_map={}),
    ):
        yield


@pytest.fixture
def test_client():
    wyvern_service = WyvernService.generate(
        route_components=[RealTimeFeatureTestingComponent],
    )
    yield TestClient(wyvern_service.service.app)


@pytest.mark.asyncio
async def test_end_to_end(mock_redis, test_client, mock_feature_store):
    response = test_client.post(
        "/api/v1/real-time-features-testing",
        json={
            "request_id": "test_request_id",
            "query": {"query": "candle"},
            "candidates": [
                {
                    "product_id": "p1",
                    "opensearch_score": 1,
                    "matched_queries": ["QUERY_1", "QUERY_2"],
                },
                {"product_id": "p2"},
                {"product_id": "p3"},
            ],
            "user": {"user_id": "1234", "user_name": "user_name"},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "feature_data": {
            "request::test_request_id": {
                "identifier": {
                    "identifier": "test_request_id",
                    "identifier_type": "request",
                },
                "features": {
                    "RealTimeNumberOfCandidatesFeature:f_number_of_candidates": 3.0,
                },
            },
            "query::candle": {
                "identifier": {"identifier": "candle", "identifier_type": "query"},
                "features": {
                    "RealTimeQueryFeature:f_query_length": 6.0,
                    "RealTimeStringFeature:f_query": "candle",
                    "RealTimeEmbeddingFeature:f_query_embedding_vector_8": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                    ],
                },
            },
            "user::1234": {
                "identifier": {"identifier": "1234", "identifier_type": "user"},
                "features": {"RealTimeUserFeature:f_user_name_length": 9.0},
            },
            "query:user::candle:1234": {
                "identifier": {
                    "identifier": "candle:1234",
                    "identifier_type": "query:user",
                },
                "features": {
                    "RealTimeUserQueryFeature:f_user_query_name_edit_distance": 3.0,
                    "RealTimeUserQueryFeature:f_user_query_name_jaccard_similarity": -3.0,
                },
            },
            "product::p1": {
                "identifier": {"identifier": "p1", "identifier_type": "product"},
                "features": {"RealTimeProductFeature:f_opensearch_score": 1.0},
            },
            "product::p2": {
                "identifier": {"identifier": "p2", "identifier_type": "product"},
                "features": {},
            },
            "product::p3": {
                "identifier": {"identifier": "p3", "identifier_type": "product"},
                "features": {},
            },
            "product:query::p1:candle": {
                "identifier": {
                    "identifier": "p1:candle",
                    "identifier_type": "product:query",
                },
                "features": {
                    "RealTimeMatchedQueriesProductFeature:f_matched_queries_QUERY_1": 1.0,
                    "RealTimeMatchedQueriesProductFeature:f_matched_queries_QUERY_2": 1.0,
                    "RealTimeQueryProductFeature:f_query_product_name_edit_distance": 4.0,
                    "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity": -4.0,
                },
            },
            "product:query::p2:candle": {
                "identifier": {
                    "identifier": "p2:candle",
                    "identifier_type": "product:query",
                },
                "features": {
                    "RealTimeQueryProductFeature:f_query_product_name_edit_distance": 4.0,
                    "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity": -4.0,
                },
            },
            "product:query::p3:candle": {
                "identifier": {
                    "identifier": "p3:candle",
                    "identifier_type": "product:query",
                },
                "features": {
                    "RealTimeQueryProductFeature:f_query_product_name_edit_distance": 4.0,
                    "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity": -4.0,
                },
            },
            "product:user::p1:1234": {
                "identifier": {
                    "identifier": "p1:1234",
                    "identifier_type": "product:user",
                },
                "features": {
                    "RealTimeUserProductFeature:f_user_product_name_edit_distance": 7.0,
                    "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity": -7.0,
                },
            },
            "product:user::p2:1234": {
                "identifier": {
                    "identifier": "p2:1234",
                    "identifier_type": "product:user",
                },
                "features": {
                    "RealTimeUserProductFeature:f_user_product_name_edit_distance": 7.0,
                    "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity": -7.0,
                },
            },
            "product:user::p3:1234": {
                "identifier": {
                    "identifier": "p3:1234",
                    "identifier_type": "product:user",
                },
                "features": {
                    "RealTimeUserProductFeature:f_user_product_name_edit_distance": 7.0,
                    "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity": -7.0,
                },
            },
        },
    }


@pytest.fixture
def mock_redis__2(mocker):
    """
    Mocks the redis call. Each entry under `return_value` corresponds to a single entity fetch from Redis
    """
    with mocker.patch(
        "wyvern.redis.wyvern_redis.mget",
        return_value=[None, None, None, None, None, None],
    ):
        yield


@pytest.mark.asyncio
async def test_end_to_end__2(mock_redis__2, test_client):
    response = test_client.post(
        "/api/v1/real-time-features-testing",
        json={
            "request_id": "test_request_id",
            "query": {"query": "candle"},
            "candidates": [
                {
                    "product_id": "p1",
                    "opensearch_score": 1,
                    "matched_queries": ["QUERY_1", "QUERY_2"],
                },
                {"product_id": "p2"},
                {"product_id": "p3"},
                {
                    "product_id": "p4",
                    "opensearch_score": 100,
                    "matched_queries": ["MATIAS", "QUERY_2"],
                },
            ],
            "user": {"user_id": "1234", "user_name": "user_name"},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "feature_data": {
            "request::test_request_id": {
                "identifier": {
                    "identifier": "test_request_id",
                    "identifier_type": "request",
                },
                "features": {
                    "RealTimeNumberOfCandidatesFeature:f_number_of_candidates": 4.0,
                },
            },
            "query::candle": {
                "identifier": {"identifier": "candle", "identifier_type": "query"},
                "features": {
                    "RealTimeQueryFeature:f_query_length": 6.0,
                    "RealTimeStringFeature:f_query": "candle",
                    "RealTimeEmbeddingFeature:f_query_embedding_vector_8": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                    ],
                },
            },
            "user::1234": {
                "identifier": {"identifier": "1234", "identifier_type": "user"},
                "features": {"RealTimeUserFeature:f_user_name_length": 9.0},
            },
            "query:user::candle:1234": {
                "identifier": {
                    "identifier": "candle:1234",
                    "identifier_type": "query:user",
                },
                "features": {
                    "RealTimeUserQueryFeature:f_user_query_name_edit_distance": 3.0,
                    "RealTimeUserQueryFeature:f_user_query_name_jaccard_similarity": -3.0,
                },
            },
            "product::p1": {
                "identifier": {"identifier": "p1", "identifier_type": "product"},
                "features": {"RealTimeProductFeature:f_opensearch_score": 1.0},
            },
            "product::p2": {
                "identifier": {"identifier": "p2", "identifier_type": "product"},
                "features": {},
            },
            "product::p3": {
                "identifier": {"identifier": "p3", "identifier_type": "product"},
                "features": {},
            },
            "product::p4": {
                "identifier": {"identifier": "p4", "identifier_type": "product"},
                "features": {"RealTimeProductFeature:f_opensearch_score": 100.0},
            },
            "product:query::p1:candle": {
                "identifier": {
                    "identifier": "p1:candle",
                    "identifier_type": "product:query",
                },
                "features": {
                    "RealTimeMatchedQueriesProductFeature:f_matched_queries_QUERY_1": 1.0,
                    "RealTimeMatchedQueriesProductFeature:f_matched_queries_QUERY_2": 1.0,
                    "RealTimeQueryProductFeature:f_query_product_name_edit_distance": 4.0,
                    "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity": -4.0,
                },
            },
            "product:query::p2:candle": {
                "identifier": {
                    "identifier": "p2:candle",
                    "identifier_type": "product:query",
                },
                "features": {
                    "RealTimeQueryProductFeature:f_query_product_name_edit_distance": 4.0,
                    "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity": -4.0,
                },
            },
            "product:query::p3:candle": {
                "identifier": {
                    "identifier": "p3:candle",
                    "identifier_type": "product:query",
                },
                "features": {
                    "RealTimeQueryProductFeature:f_query_product_name_edit_distance": 4.0,
                    "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity": -4.0,
                },
            },
            "product:query::p4:candle": {
                "identifier": {
                    "identifier": "p4:candle",
                    "identifier_type": "product:query",
                },
                "features": {
                    "RealTimeMatchedQueriesProductFeature:f_matched_queries_MATIAS": 1.0,
                    "RealTimeMatchedQueriesProductFeature:f_matched_queries_QUERY_2": 1.0,
                    "RealTimeQueryProductFeature:f_query_product_name_edit_distance": 4.0,
                    "RealTimeQueryProductFeature:f_query_product_name_jaccard_similarity": -4.0,
                },
            },
            "product:user::p1:1234": {
                "identifier": {
                    "identifier": "p1:1234",
                    "identifier_type": "product:user",
                },
                "features": {
                    "RealTimeUserProductFeature:f_user_product_name_edit_distance": 7.0,
                    "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity": -7.0,
                },
            },
            "product:user::p2:1234": {
                "identifier": {
                    "identifier": "p2:1234",
                    "identifier_type": "product:user",
                },
                "features": {
                    "RealTimeUserProductFeature:f_user_product_name_edit_distance": 7.0,
                    "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity": -7.0,
                },
            },
            "product:user::p3:1234": {
                "identifier": {
                    "identifier": "p3:1234",
                    "identifier_type": "product:user",
                },
                "features": {
                    "RealTimeUserProductFeature:f_user_product_name_edit_distance": 7.0,
                    "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity": -7.0,
                },
            },
            "product:user::p4:1234": {
                "identifier": {
                    "identifier": "p4:1234",
                    "identifier_type": "product:user",
                },
                "features": {
                    "RealTimeUserProductFeature:f_user_product_name_edit_distance": 7.0,
                    "RealTimeUserProductFeature:f_user_product_name_jaccard_similarity": -7.0,
                },
            },
        },
    }


def test_separate_real_time_features():
    realtime_features, non_realtime_features = separate_real_time_features(
        [
            "RealTimeProductFeature:f_opensearch_score",
            "RankingRealtimeFeatureComponent:f_1",
            "RankingRealtimeFeatureComponent:f_3",
            "random_fv:fn1",
        ],
    )
    assert realtime_features == [
        "RealTimeProductFeature:f_opensearch_score",
        "RankingRealtimeFeatureComponent:f_1",
        "RankingRealtimeFeatureComponent:f_3",
    ]
    assert non_realtime_features == ["random_fv:fn1"]
