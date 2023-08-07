# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, List, Optional, Sequence

from redis.asyncio import Redis

from wyvern.config import settings
from wyvern.core.compression import wyvern_decode, wyvern_encode
from wyvern.utils import generate_index_key
from wyvern.wyvern_request import WyvernRequest

logger = logging.getLogger(__name__)

REDIS_BATCH_SIZE = settings.REDIS_BATCH_SIZE


class WyvernRedis:
    """
    WyvernRedis is a wrapper for redis client to help index your entities in redis with Wyvern's convention
    """

    def __init__(
        self,
        scope: str = "",
        redis_host: Optional[str] = None,
        redis_port: Optional[int] = None,
    ) -> None:
        """
        scope is used to prefix the redis key. You can use the environment variable PROJECT_NAME to set the scope.
        """
        host = redis_host or settings.REDIS_HOST
        if not host:
            raise ValueError("redis host is not set or found in environment variable")
        port = redis_port or settings.REDIS_PORT
        if not port:
            raise ValueError("redis port is not set or found in environment variable")
        self.redis_connection: Redis = Redis(
            host=host,
            port=port,
        )
        self.key_prefix = scope or settings.PROJECT_NAME

    # TODO (shu): This entire file shouldn't be called redis.py -- this is specific to indexing
    # We should actually have a redis.py file that does any of the required logic.. and mock that at most
    async def bulk_index(
        self,
        entities: List[Dict[str, Any]],
        entity_key: str,
        entity_type: str,
    ) -> List[str]:
        if not entities:
            return []
        mapping = {
            generate_index_key(
                self.key_prefix,
                entity_type,
                entity[entity_key],
            ): wyvern_encode(entity)
            for entity in entities
        }
        await self.redis_connection.mset(mapping=mapping)  # type: ignore
        return [entity[entity_key] for entity in entities]

    async def get(self, index_key: str) -> Optional[str]:
        return await self.redis_connection.get(index_key)

    async def mget(self, index_keys: List[str]) -> List[Optional[str]]:
        if not index_keys:
            return []
        return await self.redis_connection.mget(index_keys)

    async def mget_json(
        self,
        index_keys: List[str],
    ) -> List[Optional[Dict[str, Any]]]:
        results = await self.mget(index_keys)
        return [wyvern_decode(val) if val is not None else None for val in results]

    async def mget_update_in_place(
        self,
        index_keys: List[str],
        wyvern_request: WyvernRequest,
    ) -> None:
        # single mget way
        results = await self.mget(index_keys)
        wyvern_request.entity_store = {
            key: wyvern_decode(val) if val is not None else None
            for key, val in zip(index_keys, results)
        }

    async def get_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        get entity from redis
        """
        index_key = generate_index_key(
            self.key_prefix,
            entity_type,
            entity_id,
        )

        encoded_entity = await self.get(index_key)
        if not encoded_entity:
            return None
        return wyvern_decode(encoded_entity)

    async def get_entities(
        self,
        entity_type: str,
        entity_ids: Sequence[str],
    ) -> List[Optional[Dict[str, Any]]]:
        """
        get entity from redis
        """
        index_keys = [
            generate_index_key(self.key_prefix, entity_type, entity_id)
            for entity_id in entity_ids
        ]
        if not index_keys:
            return []
        return await self.mget_json(index_keys)

    async def delete_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> None:
        """
        delete entity from redis
        """
        index_key = generate_index_key(self.key_prefix, entity_type, entity_id)
        await self.redis_connection.delete(index_key)

    async def delete_entities(
        self,
        entity_type: str,
        entity_ids: Sequence[str],
    ) -> None:
        """
        delete entities from redis
        """
        index_keys = [
            generate_index_key(self.key_prefix, entity_type, entity_id)
            for entity_id in entity_ids
        ]
        await self.redis_connection.delete(*index_keys)


wyvern_redis = WyvernRedis()
