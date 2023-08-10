# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class BaseExperimentationProvider(ABC):
    """
    A base class for experimentation providers.
    All providers should inherit from this and implement the necessary methods.
    """

    @abstractmethod
    def get_result(self, experiment_id: str, entity_id: str, **kwargs) -> str:
        """
        Get the result (variant) for a given experiment and entity.

        Args:
        - experiment_id (str): The unique ID of the experiment.
        - entity_id (str): The unique ID of the entity.
        - kwargs (dict): Any additional arguments to pass to the provider for targeting.

        Returns:
        - str: The result (variant) assigned to the entity for the specified experiment.
        """
        raise NotImplementedError

    @abstractmethod
    def log_result(
        self, experiment_id: str, entity_id: str, variant: str, **kwargs
    ) -> None:
        """
        Log the result (variant) for a given experiment and entity.

        Args:
        - experiment_id (str): The unique ID of the experiment.
        - entity_id (str): The unique ID of the entity.
        - variant (str): The result (variant) assigned to the entity for the specified experiment.
        - kwargs (dict): Any additional arguments to pass to the provider for targeting.

        Returns:
        - None
        """
        raise NotImplementedError