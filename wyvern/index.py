# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Sequence

from wyvern.redis import wyvern_redis


class WyvernIndex:
    @classmethod
    async def get(cls, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        return await wyvern_redis.get_entity(
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @classmethod
    async def bulk_get(
        cls,
        entity_type: str,
        entity_ids: Sequence[str],
    ) -> List[Optional[Dict[str, Any]]]:
        if not entity_ids:
            return []
        return await wyvern_redis.get_entities(
            entity_type=entity_type,
            entity_ids=entity_ids,
        )

    @classmethod
    async def delete(cls, entity_type: str, entity_id: str) -> None:
        await wyvern_redis.delete_entity(
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @classmethod
    async def bulk_delete(
        cls,
        entity_type: str,
        entity_ids: Sequence[str],
    ) -> None:
        if not entity_ids:
            return
        await wyvern_redis.delete_entities(
            entity_type=entity_type,
            entity_ids=entity_ids,
        )


class WyvernEntityIndex:
    @classmethod
    async def get(
        cls,
        entity_type: str,
        entity_id: str,
    ) -> Optional[Dict[str, Any]]:
        return await WyvernIndex.get(
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @classmethod
    async def bulk_get(
        cls,
        entity_type: str,
        entity_ids: Sequence[str],
    ) -> List[Optional[Dict[str, Any]]]:
        return await WyvernIndex.bulk_get(
            entity_type=entity_type,
            entity_ids=entity_ids,
        )

    @classmethod
    async def delete(cls, entity_type: str, entity_id: str) -> None:
        await WyvernIndex.delete(
            entity_type=entity_type,
            entity_id=entity_id,
        )

    @classmethod
    async def bulk_delete(
        cls,
        entity_type: str,
        entity_ids: Sequence[str],
    ) -> None:
        await WyvernIndex.bulk_delete(
            entity_type=entity_type,
            entity_ids=entity_ids,
        )
