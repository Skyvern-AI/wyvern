# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Generic

from pydantic.generics import GenericModel
from pydantic.main import BaseModel

from wyvern import request_context
from wyvern.components.component import Component
from wyvern.components.events.events import EventType, LoggedEvent
from wyvern.entities.feature_entities import IDENTIFIER
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
        feature_df: The feature data frame to log.
    """

    request: REQUEST_ENTITY

    class Config:
        arbitrary_types_allowed = True


class FeatureEventLoggingComponent(
    Component[FeatureEventLoggingRequest[REQUEST_ENTITY], None],
    Generic[REQUEST_ENTITY],
):
    """A component that logs feature events."""

    async def execute(
        self, input: FeatureEventLoggingRequest[REQUEST_ENTITY], **kwargs
    ) -> None:
        """Logs feature events."""
        wyvern_request = request_context.ensure_current_request()
        url_path = wyvern_request.url_path
        run_id = wyvern_request.run_id

        def feature_event_generator():
            """Generates feature events. This is a generator function that's called by the event logger. It's never called directly.

            Returns:
                A list of feature events.
            """
            timestamp = datetime.utcnow()

            # Extract column names excluding "IDENTIFIER"
            feature_columns = wyvern_request.feature_df.df.columns[1:]

            return [
                FeatureEvent(
                    request_id=input.request.request_id,
                    run_id=run_id,
                    api_source=url_path,
                    event_timestamp=timestamp,
                    event_data=FeatureLogEventData(
                        feature_identifier_type=wyvern_request.get_original_identifier(
                            row[IDENTIFIER],
                            col,
                        ).identifier_type,
                        feature_identifier=wyvern_request.get_original_identifier(
                            row[IDENTIFIER],
                            col,
                        ).identifier,
                        feature_name=col,
                        feature_value=row[col],
                    ),
                )
                for row in wyvern_request.feature_df.df.iter_rows(named=True)
                for col in feature_columns
                if row[col]
            ]

        event_logger.log_events(feature_event_generator)  # type: ignore
