# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from wyvern.entities.identifier import SimpleIdentifierType

MIN_INDEX_ITEMS = 0
MAX_INDEX_ITEMS = 1000


class IndexResponse(BaseModel):
    entity_type: str
    entity_ids: List[str]


class IndexRequest(BaseModel):
    entities: List[Dict[Any, Any]] = Field(
        min_items=MIN_INDEX_ITEMS,
        max_items=MAX_INDEX_ITEMS,
    )
    entity_type: SimpleIdentifierType
    entity_key: Optional[str]


class EntitiesRequest(BaseModel):
    entity_ids: List[str] = Field(
        min_items=MIN_INDEX_ITEMS,
        max_items=MAX_INDEX_ITEMS,
    )
    entity_type: SimpleIdentifierType


class DeleteEntitiesRequest(EntitiesRequest):
    pass


class GetEntitiesResponse(BaseModel):
    entity_type: str
    entities: Dict[str, Optional[Dict[Any, Any]]] = Field(default_factory=dict)


class DeleteEntitiesResponse(BaseModel):
    entity_type: str
    entity_ids: List[str]
