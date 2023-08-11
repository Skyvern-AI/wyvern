# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict

from pydantic import BaseModel

from wyvern.components.events.events import EventType, LoggedEvent


class ExperimentationEventData(BaseModel):
    experiment_id: str
    entity_id: str
    result: str
    timestamp: datetime
    metadata: Dict


class ExperimentationEvent(LoggedEvent[ExperimentationEventData]):
    event_type: EventType = EventType.EXPERIMENTATION
