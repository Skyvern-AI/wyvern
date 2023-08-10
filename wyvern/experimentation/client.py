# -*- coding: utf-8 -*-
from .providers.eppo_provider import EppoExperimentationClient


class ExperimentationClient:
    def __init__(self, provider_name: str):
        """
        Initializes the ExperimentationClient with a specified provider.

        Args:
        - provider_name (str): The name of the experimentation provider (e.g., "eppo").
        """
        if provider_name == "eppo":
            self.provider = EppoExperimentationClient()
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def get_experiment_result(
        self, experiment_id: str, entity_id: str, **kwargs
    ) -> str:
        """
        Get the result (variant) for a given experiment and entity using the chosen provider.

        Args:
        - experiment_id (str): The unique ID of the experiment.
        - entity_id (str): The unique ID of the entity.
        - kwargs (dict): Any additional arguments to pass to the provider for targeting.

        Returns:
        - str: The result (variant) assigned to the entity for the specified experiment.
        """
        # TODO (kerem): What happens if the provider is down / returns None?
        #  We should also enforce defining a default value for each experiment to return in such cases.
        result = self.provider.get_result(experiment_id, entity_id, **kwargs)
        self.provider.log_result(experiment_id, entity_id, result, **kwargs)
        return result
