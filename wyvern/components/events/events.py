# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

EVENT_DATA = TypeVar("EVENT_DATA", bound=BaseModel)


class EventType(str, Enum):
    """Enum for the different types of events that can be logged."""

    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    CANDIDATE = "CANDIDATE"
    FEATURE = "FEATURE"
    MODEL = "MODEL"
    IMPRESSION = "IMPRESSION"
    EXPERIMENTATION = "EXPERIMENTATION"
    CUSTOM = "CUSTOM"


class LoggedEvent(GenericModel, Generic[EVENT_DATA]):
    """Base class for all logged events.

    Attributes:
        request_id: The request ID of the request that triggered the event.
        api_source: The API source of the request that triggered the event.
        event_timestamp: The timestamp of the event.
        event_type: The type of the event.
        event_data: The data associated with the event. This is a generic type that can be any subclass of BaseModel.
    """

    request_id: Optional[str]
    api_source: Optional[str]
    event_timestamp: Optional[datetime]
    event_type: EventType
    event_data: EVENT_DATA


class EntityEventData(BaseModel):
    """Base class for all entity event data.

    Attributes:
        entity_identifier: The identifier of the entity that the event is associated with.
        entity_identifier_type: The type of the entity identifier.
    """

    entity_identifier: str
    entity_identifier_type: str


ENTITY_EVENT_DATA_TYPE = TypeVar("ENTITY_EVENT_DATA_TYPE", bound=EntityEventData)


class CustomEvent(LoggedEvent[ENTITY_EVENT_DATA_TYPE]):
    """Class for custom events. Custom event data must be a subclass of EntityEventData.

    Attributes:
        event_type: The type of the event. This is always EventType.CUSTOM.
    """

    event_type: EventType = EventType.CUSTOM
