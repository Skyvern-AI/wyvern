# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Generic

from pydantic.generics import GenericModel
from pydantic.main import BaseModel

from wyvern import request_context
from wyvern.components.component import Component
from wyvern.components.events.events import EventType, LoggedEvent
from wyvern.entities.feature_entities import FeatureMap
from wyvern.event_logging import event_logger
from wyvern.wyvern_typing import REQUEST_ENTITY, WyvernFeature


class FeatureLogEventData(BaseModel):
    feature_identifier: str
    feature_identifier_type: str
    feature_name: str
    feature_value: WyvernFeature


class FeatureEvent(LoggedEvent[FeatureLogEventData]):
    event_type: EventType = EventType.FEATURE


class FeatureEventLoggingRequest(
    GenericModel,
    Generic[REQUEST_ENTITY],
):
    request: REQUEST_ENTITY
    feature_map: FeatureMap


class FeatureEventLoggingComponent(
    Component[FeatureEventLoggingRequest[REQUEST_ENTITY], None],
    Generic[REQUEST_ENTITY],
):
    async def execute(
        self, input: FeatureEventLoggingRequest[REQUEST_ENTITY], **kwargs
    ) -> None:
        url_path = request_context.ensure_current_request().url_path

        def feature_event_generator():
            timestamp = datetime.utcnow()
            return [
                FeatureEvent(
                    request_id=input.request.request_id,
                    api_source=url_path,
                    event_timestamp=timestamp,
                    event_data=FeatureLogEventData(
                        feature_identifier=feature_data.identifier.identifier,
                        feature_identifier_type=feature_data.identifier.identifier_type,
                        feature_name=feature_name,
                        feature_value=feature_value,
                    ),
                )
                for feature_data in input.feature_map.feature_map.values()
                for feature_name, feature_value in feature_data.features.items()
            ]

        event_logger.log_events(feature_event_generator)  # type: ignore
