# -*- coding: utf-8 -*-
from typing import Optional

from wyvern.exceptions import ExperimentationProviderNotSupportedError
from wyvern.experimentation.providers.base import ExperimentationProvider
from wyvern.experimentation.providers.eppo_provider import EppoExperimentationClient


class ExperimentationClient:
    def __init__(self, provider_name: str):
        """
        Initializes the ExperimentationClient with a specified provider.

        Args:
        - provider_name (str): The name of the experimentation provider (e.g., "eppo").
        """
        if provider_name == ExperimentationProvider.EPPO:
            self.provider = EppoExperimentationClient()
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
        result = None
        error_message = None

        try:
            result = self.provider.get_result(experiment_id, entity_id, **kwargs)
        except Exception as e:
            error_message = str(e)

        self.provider.log_result(
            experiment_id, entity_id, result, error_message, **kwargs
        )
        return result
