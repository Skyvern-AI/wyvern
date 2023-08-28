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
    """Data for a feature event.

    Attributes:
        feature_identifier: The identifier of the feature.
        feature_identifier_type: The type of the feature identifier.
        feature_name: The name of the feature.
        feature_value: The value of the feature.
    """

    feature_identifier: str
    feature_identifier_type: str
    feature_name: str
    feature_value: WyvernFeature


class FeatureEvent(LoggedEvent[FeatureLogEventData]):
    """A feature event.

    Attributes:
        event_type: The type of the event. Defaults to EventType.FEATURE.
    """

    event_type: EventType = EventType.FEATURE


class FeatureEventLoggingRequest(
    GenericModel,
    Generic[REQUEST_ENTITY],
):
    """A request to log feature events.

    Attributes:
        request: The request to log feature events for.
        feature_map: The feature map to log.
    """

    request: REQUEST_ENTITY
    feature_map: FeatureMap


class FeatureEventLoggingComponent(
    Component[FeatureEventLoggingRequest[REQUEST_ENTITY], None],
    Generic[REQUEST_ENTITY],
):
    """A component that logs feature events."""

    async def execute(
        self, input: FeatureEventLoggingRequest[REQUEST_ENTITY], **kwargs
    ) -> None:
        """Logs feature events."""
        url_path = request_context.ensure_current_request().url_path

        def feature_event_generator():
            """Generates feature events. This is a generator function that's called by the event logger. It's never called directly.

            Returns:
                A list of feature events.
            """
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
