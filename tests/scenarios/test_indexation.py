# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient

from wyvern.service import WyvernService

PRODUCT_ENTITY_1 = {
    "product_id": "1",
    "product_name": "test_product1",
    "product_description": "test_product1_description",
}
PRODUCT_ENTITY_2 = {
    "product_id": "2",
    "product_name": "test_product2",
    "product_description": "test_product2_description",
}

PRODUCT_ENTITY_1_WITH_ID = {
    "id": "1",
    "product_name": "test_product1",
    "product_description": "test_product1_description",
}
PRODUCT_ENTITY_2_WITH_ID = {
    "id": "2",
    "product_name": "test_product2",
    "product_description": "test_product2_description",
}


@pytest.fixture
def mock_redis(mocker):
    with mocker.patch(
        "wyvern.redis.wyvern_redis.bulk_index",
        return_value=["1", "2"],
    ), mocker.patch(
        "wyvern.redis.wyvern_redis.get_entity",
        return_value=PRODUCT_ENTITY_1,
    ), mocker.patch(
        "wyvern.redis.wyvern_redis.get_entities",
        return_value=[
            PRODUCT_ENTITY_1,
            PRODUCT_ENTITY_2,
        ],
    ), mocker.patch(
        "wyvern.redis.wyvern_redis.delete_entity",
    ), mocker.patch(
        "wyvern.redis.wyvern_redis.delete_entities",
    ):
        yield


@pytest.fixture
def test_client(mock_redis):
    wyvern_service = WyvernService.generate()
    yield TestClient(wyvern_service.service.app)


@pytest.mark.asyncio
async def test_product_upload(test_client):
    response = test_client.post(
        "/api/v1/entities/upload",
        json={
            "entities": [
                PRODUCT_ENTITY_1,
                PRODUCT_ENTITY_2,
            ],
            "entity_type": "product",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "entity_type": "product",
        "entity_ids": ["1", "2"],
    }


@pytest.mark.asyncio
async def test_product_upload__with_different_entity_key(test_client):
    response = test_client.post(
        "/api/v1/entities/upload",
        json={
            "entities": [
                PRODUCT_ENTITY_1_WITH_ID,
                PRODUCT_ENTITY_2_WITH_ID,
            ],
            "entity_type": "product",
            "entity_key": "id",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "entity_type": "product",
        "entity_ids": ["1", "2"],
    }


@pytest.mark.asyncio
async def test_get_products(test_client):
    response = test_client.post(
        "/api/v1/entities/get",
        json={
            "entity_ids": ["1", "2"],
            "entity_type": "product",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "entity_type": "product",
        "entities": {
            "1": PRODUCT_ENTITY_1,
            "2": PRODUCT_ENTITY_2,
        },
    }


@pytest.mark.asyncio
async def test_delete_products(test_client):
    response = test_client.post(
        "/api/v1/entities/delete",
        json={
            "entity_ids": ["1", "2"],
            "entity_type": "product",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "entity_type": "product",
        "entity_ids": ["1", "2"],
    }
