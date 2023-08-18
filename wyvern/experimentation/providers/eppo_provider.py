# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional

import eppo_client  # type: ignore
from eppo_client.assignment_logger import AssignmentLogger  # type: ignore
from eppo_client.config import Config  # type: ignore

from wyvern import request_context
from wyvern.components.events.events import LoggedEvent
from wyvern.config import settings
from wyvern.event_logging import event_logger
from wyvern.exceptions import ExperimentationClientInitializationError
from wyvern.experimentation.experimentation_logging import (
    ExperimentationEvent,
    ExperimentationEventData,
)
from wyvern.experimentation.providers.base import (
    BaseExperimentationProvider,
    ExperimentationProvider,
)


class EppoExperimentationClient(BaseExperimentationProvider):
    """
    An experimentation client specifically for the Eppo platform.

    Extends the BaseExperimentationProvider to provide functionality using the Eppo client.

    Methods:
    - __init__() -> None
    - get_result(experiment_id: str, entity_id: str, **kwargs) -> str
    - log_result(experiment_id: str, entity_id: str, variant: str) -> None
    """

    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or settings.EPPO_API_KEY
        # AssignmentLogger is a dummy logger that does not log anything.
        # We handle logging ourselves in the log_result method.
        try:
            client_config = Config(
                api_key=api_key,
                assignment_logger=AssignmentLogger(),
            )
            eppo_client.init(client_config)
        except Exception as e:
            raise ExperimentationClientInitializationError(
                provider_name=ExperimentationProvider.EPPO.value,
                error=e,
            )

    def get_result(self, experiment_id: str, entity_id: str, **kwargs) -> str:
        """
        Fetches the variant for a given experiment and entity from the Eppo client.

        Args:
        - experiment_id (str): The unique ID of the experiment.
        - entity_id (str): The unique ID of the entity (e.g., user or other subject).
        - **kwargs: Additional arguments to be passed to the Eppo client's get_assignment method.

        Returns:
        - str: The assigned variant for the given experiment and entity.
        """
        client = eppo_client.get_instance()
        return client.get_assignment(entity_id, experiment_id, kwargs)

    def log_result(
        self,
        experiment_id: str,
        entity_id: str,
        variant: Optional[str] = None,
        has_error: bool = False,
        **kwargs
    ) -> None:
        """
        Logs the result for a given experiment and entity.

        Args:
        - experiment_id (str): The unique ID of the experiment.
        - entity_id (str): The unique ID of the entity.
        - variant (str): The assigned variant for the given experiment and entity.

        Note: This method is overridden to do nothing because the assignment logger we set in Eppo already
        handles result logging upon assignment.
        """

        request = request_context.ensure_current_request()

        def event_generator() -> List[LoggedEvent[ExperimentationEventData]]:
            timestamp = datetime.utcnow()
            request_id = request.request_id
            api_source = request.url_path

            return [
                ExperimentationEvent(
                    request_id=request_id,
                    api_source=api_source,
                    event_timestamp=timestamp,
                    event_data=ExperimentationEventData(
                        experiment_id=experiment_id,
                        entity_id=entity_id,
                        result=variant,
                        timestamp=timestamp,
                        metadata=kwargs,
                        has_error=has_error,
                    ),
                ),
            ]

        event_logger.log_events(event_generator)
