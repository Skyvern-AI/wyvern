# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, Dict, List, Type

from wyvern.components.api_route_component import APIRouteComponent
from wyvern.entities.index_entities import (
    DeleteEntitiesRequest,
    DeleteEntitiesResponse,
    EntitiesRequest,
    GetEntitiesResponse,
    IndexRequest,
    IndexResponse,
)
from wyvern.exceptions import WyvernEntityValidationError, WyvernError
from wyvern.index import WyvernEntityIndex, WyvernIndex
from wyvern.redis import wyvern_redis

logger = logging.getLogger(__name__)


class IndexUploadComponent(
    APIRouteComponent[IndexRequest, IndexResponse],
):
    PATH: str = "/entities/upload"
    REQUEST_SCHEMA_CLASS: Type[IndexRequest] = IndexRequest
    RESPONSE_SCHEMA_CLASS: Type[IndexResponse] = IndexResponse

    async def execute(
        self,
        input: IndexRequest,
        **kwargs,
    ) -> IndexResponse:
        """
        bulk index entities with redis pipeline
        """

        entity_internal_key = f"{input.entity_type.value}_id"
        entity_key: str = input.entity_key or entity_internal_key

        entities: List[Dict[str, Any]] = []
        for entity in input.entities:
            # validation: entity must have entity_key
            if entity_key not in entity:
                raise WyvernEntityValidationError(
                    entity_key=entity_key,
                    entity=entity,
                )

            if entity_internal_key not in entity:
                entity[entity_internal_key] = entity[entity_key]
            elif (entity_internal_key in entity) and (
                entity[entity_internal_key] != entity[entity_key]
            ):
                logger.warning(
                    f"entity already has an internal key={entity_internal_key} "
                    f"with value={entity[entity_internal_key]}, "
                    f"skipping setting the value to {entity[entity_key]}",
                )

            entities.append(entity)

        entity_ids = await wyvern_redis.bulk_index(
            entities,
            entity_key,
            input.entity_type.value,
        )

        return IndexResponse(
            entity_type=input.entity_type.value,
            entity_ids=entity_ids,
        )


class IndexDeleteComponent(
    APIRouteComponent[DeleteEntitiesRequest, DeleteEntitiesResponse],
):
    PATH: str = "/entities/delete"
    REQUEST_SCHEMA_CLASS: Type[DeleteEntitiesRequest] = DeleteEntitiesRequest
    RESPONSE_SCHEMA_CLASS: Type[DeleteEntitiesResponse] = DeleteEntitiesResponse

    async def execute(
        self,
        input: DeleteEntitiesRequest,
        **kwargs,
    ) -> DeleteEntitiesResponse:
        await WyvernIndex.bulk_delete(input.entity_type.value, input.entity_ids)
        return DeleteEntitiesResponse(
            entity_ids=input.entity_ids,
            entity_type=input.entity_type.value,
        )


class IndexGetComponent(
    APIRouteComponent[EntitiesRequest, GetEntitiesResponse],
):
    PATH: str = "/entities/get"
    REQUEST_SCHEMA_CLASS: Type[EntitiesRequest] = EntitiesRequest
    RESPONSE_SCHEMA_CLASS: Type[GetEntitiesResponse] = GetEntitiesResponse

    async def execute(
        self,
        input: EntitiesRequest,
        **kwargs,
    ) -> GetEntitiesResponse:
        entities = await WyvernEntityIndex.bulk_get(
            entity_type=input.entity_type.value,
            entity_ids=input.entity_ids,
        )
        if len(entities) != len(input.entity_ids):
            raise WyvernError("Unexpected Error")
        entity_map = {input.entity_ids[i]: entities[i] for i in range(len(entities))}
        return GetEntitiesResponse(
            entity_type=input.entity_type.value,
            entities=entity_map,
        )
