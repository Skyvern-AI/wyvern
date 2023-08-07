# -*- coding: utf-8 -*-
from wyvern.config import settings


def generate_index_key(
    scope: str,
    entity_type: str,
    entity_id: str,
) -> str:
    return f"{scope}:{settings.WYVERN_INDEX_VERSION}:{entity_type}:{entity_id}"
