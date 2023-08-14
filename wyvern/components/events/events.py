# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

EVENT_DATA = TypeVar("EVENT_DATA", bound=BaseModel)


class EventType(str, Enum):
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    CANDIDATE = "CANDIDATE"
    FEATURE = "FEATURE"
    MODEL = "MODEL"
    IMPRESSION = "IMPRESSION"
    EXPERIMENTATION = "EXPERIMENTATION"
    CUSTOM = "CUSTOM"


class LoggedEvent(GenericModel, Generic[EVENT_DATA]):
    request_id: Optional[str]
    api_source: Optional[str]
    event_timestamp: Optional[datetime]
    event_type: EventType
    event_data: EVENT_DATA


class EntityEventData(BaseModel):
    entity_identifier: str
    entity_identifier_type: str


ENTITY_EVENT_DATA_TYPE = TypeVar("ENTITY_EVENT_DATA_TYPE", bound=EntityEventData)


class CustomEvent(LoggedEvent[ENTITY_EVENT_DATA_TYPE]):
    event_type: EventType = EventType.CUSTOM
