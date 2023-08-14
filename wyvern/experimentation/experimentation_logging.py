# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from wyvern.components.events.events import EventType, LoggedEvent


class ExperimentationEventData(BaseModel):
    experiment_id: str
    entity_id: str
    result: Optional[str]
    timestamp: datetime
    metadata: Dict
    has_error: bool


class ExperimentationEvent(LoggedEvent[ExperimentationEventData]):
    event_type: EventType = EventType.EXPERIMENTATION
