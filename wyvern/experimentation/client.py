# -*- coding: utf-8 -*-
import logging
import traceback
from typing import Optional

from wyvern.config import settings
from wyvern.exceptions import ExperimentationProviderNotSupportedError
from wyvern.experimentation.providers.base import ExperimentationProvider
from wyvern.experimentation.providers.eppo_provider import EppoExperimentationClient

logger = logging.getLogger(__name__)


class ExperimentationClient:
    """
    A client for interacting with experimentation providers.
    """

    def __init__(self, provider_name: str, api_key: Optional[str] = None):
        """
        Initializes the ExperimentationClient with a specified provider.

        Args:
        - provider_name (str): The name of the experimentation provider (e.g., "eppo").
        """
        if not settings.EXPERIMENTATION_ENABLED:
            logger.info("Experimentation is disabled")
            self.enabled = False
            return

        self.enabled = True
        if provider_name == ExperimentationProvider.EPPO.value:
            logger.info("Using EPPO experimentation provider")
            self.provider = EppoExperimentationClient(api_key=api_key)
        else:
            raise ExperimentationProviderNotSupportedError(provider_name=provider_name)

    def get_experiment_result(
        self, experiment_id: str, entity_id: str, **kwargs
    ) -> Optional[str]:
        """
        Get the result (variant) for a given experiment and entity using the chosen provider.

        Args:
        - experiment_id (str): The unique ID of the experiment.
        - entity_id (str): The unique ID of the entity.
        - kwargs (dict): Any additional arguments to pass to the provider for targeting.

        Returns:
        - str: The result (variant) assigned to the entity for the specified experiment.
        """
        if not self.enabled:
            logger.error(
                "get_experiment_result called when experimentation is disabled",
            )
            return None

        result = None
        has_error = False

        try:
            result = self.provider.get_result(experiment_id, entity_id, **kwargs)
        except Exception:
            logger.exception(
                f"Error getting experiment result. Experiment ID: {experiment_id}, Entity ID: {entity_id} | "
                f"{traceback.format_exc()}",
            )
            has_error = True

        self.provider.log_result(experiment_id, entity_id, result, has_error, **kwargs)
        return result


experimentation_client = ExperimentationClient(
    provider_name=settings.EXPERIMENTATION_PROVIDER,
)
