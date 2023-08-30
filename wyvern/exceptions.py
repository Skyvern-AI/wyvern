# -*- coding: utf-8 -*-
from typing import Optional

from wyvern import request_context


class WyvernError(Exception):
    """Base class for all Wyvern errors.

    Attributes:
        message: The error message.
        error_code: The error code.
    """

    message = "Wyvern error"

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: int = 0,
        **kwargs,
    ) -> None:
        self.error_code = error_code
        if message:
            self.message = message
        try:
            self._error_string = self.message.format(**kwargs)
        except Exception:
            # at least get the core message out if something happened
            self._error_string = self.message
        wyvern_request = request_context.current()
        request_id = None
        if wyvern_request and wyvern_request.request_id:
            request_id = wyvern_request.request_id
        elif "request_id" in kwargs:
            request_id = kwargs["request_id"]

        self.request_id = request_id
        if self.request_id:
            self._error_string = f"[request_id={self.request_id}] {self._error_string}"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self._error_string}"


class WyvernEntityValidationError(WyvernError):
    """
    Raised when entity data is invalid
    """

    message = "{entity_key} is missing in entity data: {entity}"


class PaginationError(WyvernError):
    """
    Raised when there is an error in pagination
    """

    pass


class WyvernRouteRegistrationError(WyvernError):
    """
    Raised when there is an error in registering a route
    """

    message = (
        "WyvernRouteRegistrationError: Invalid component: {component}. To register a route, "
        "the component must be a subclass of APIComponentRoute"
    )


class ComponentAlreadyDefinedInPipelineComponentError(WyvernError):
    """
    Raised when a component is already defined in a pipeline component
    """

    message = "'{component_type}' is already defined by the PipelineComponent. It cannot be passed as an upstream!"


class WyvernFeatureStoreError(WyvernError):
    """
    Raised when there is an error in feature store
    """

    message = "Received error from feature store: {error}"


class WyvernFeatureNameError(WyvernError):
    """
    Raised when there is an error in feature name
    """

    message = (
        "Invalid online feature names: {invalid_feature_names}. "
        "feature references must have format 'feature_view:feature', e.g. customer_fv:daily_transactions. "
        "Are these realtime features? Make sure you define realtime feature component and register them."
    )


class WyvernModelInputError(WyvernError):
    """
    Raised when there is an error in model input
    """

    message = (
        "Invalid ModelInput: {model_input}"
        "ModelInput.entities must contain at least one entity."
    )


class WyvernModelbitTokenMissingError(WyvernError):
    """
    Raised when modelbit token is missing
    """

    message = "Modelbit authentication token is required."


class WyvernModelbitValidationError(WyvernError):
    """
    Raised when modelbit validation fails
    """

    message = "Generated modelbit requests length does not match the number of target entities."


class WyvernAPIKeyMissingError(WyvernError):
    """
    Raised when api key is missing
    """

    message = (
        "Wyvern api key is missing. "
        "Pass api_key to WyvernAPI or define WYVERN_API_KEY in your environment."
    )


class ExperimentationProviderNotSupportedError(WyvernError):
    """
    Raised when experimentation provider is not supported
    """

    message = "Received error from feature store: {provider_name}"


class ExperimentationClientInitializationError(WyvernError):
    """
    Raised when experimentation client initialization fails
    """

    message = "Failed to initialize experimentation client for provider: {provider_name}, {error}"


class EntityColumnMissingError(WyvernError):
    message = "Entity column {entity} is missing in the entity data"
