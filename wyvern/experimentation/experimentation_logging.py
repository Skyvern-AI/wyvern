# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from wyvern.components.events.events import EventType, LoggedEvent


class ExperimentationEventData(BaseModel):
    """
    Data class for ExperimentationEvent.

    Attributes:
        experiment_id: The experiment id.
        entity_id: The entity id.
        result: The result of the experiment. Can be None.
        timestamp: The timestamp of the event.
        metadata: The metadata of the event such as targeting parameters etc.
        has_error: Whether the request has errored or not.
    """

    experiment_id: str
    entity_id: str
    result: Optional[str]
    timestamp: datetime
    metadata: Dict
    has_error: bool


class ExperimentationEvent(LoggedEvent[ExperimentationEventData]):
    """
    Event class for ExperimentationEvent.

    Attributes:
        event_type: The event type. This is always EventType.EXPERIMENTATION.
    """

    event_type: EventType = EventType.EXPERIMENTATION
