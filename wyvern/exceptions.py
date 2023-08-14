# -*- coding: utf-8 -*-
from typing import Optional


class WyvernError(Exception):
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

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self._error_string}"


class WyvernEntityValidationError(WyvernError):
    message = "{entity_key} is missing in entity data: {entity}"


class PaginationError(WyvernError):
    pass


class WyvernRouteRegistrationError(WyvernError):
    message = (
        "WyvernRouteRegistrationError: Invalid component: {component}. To register a route, "
        "the component must be a subclass of APIComponentRoute"
    )


class WyvernFeatureStoreError(WyvernError):
    message = "Received error from feature store: {error}"


class WyvernFeatureNameError(WyvernError):
    message = (
        "Invalid online feature names: {invalid_feature_names}. "
        "feature references must have format 'feature_view:feature', e.g. customer_fv:daily_transactions. "
        "Are these realtime features? Make sure you define realtime feature component and register them."
    )


class WyvernModelInputError(WyvernError):
    message = (
        "Invalid ModelInput: {model_input}"
        "ModelInput.entities must contain at least one entity."
    )


class WyvernModelbitTokenMissingError(WyvernError):
    message = "Modelbit authentication token is required."


class WyvernModelbitValidationError(WyvernError):
    message = "Generated modelbit requests length does not match the number of target entities."


class WyvernAPIKeyMissingError(WyvernError):
    message = (
        "Wyvern api key is missing. "
        "Pass api_key to WyvernAPI or define WYVERN_API_KEY in your environment."
    )


class ExperimentationProviderNotSupportedError(WyvernError):
    message = "Received error from feature store: {provider_name}"


class ExperimentationClientInitializationError(WyvernError):
    message = "Failed to initialize experimentation client for provider: {provider_name}, {error}"
