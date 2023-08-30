# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import logging
from enum import Enum
from functools import cached_property
from typing import Dict, Generic, Optional, Set
from uuid import uuid4

from wyvern import request_context
from wyvern.entities.identifier import Identifier
from wyvern.wyvern_typing import INPUT_TYPE, OUTPUT_TYPE, WyvernFeature

logger = logging.getLogger(__name__)


class ComponentStatus(str, Enum):
    """
    This enum defines the status of the component.
    """

    created = "created"
    initialized = "initialized"
    failed = "failed"


class Component(Generic[INPUT_TYPE, OUTPUT_TYPE]):
    """
    Component is the base class for all the components in Wyvern. It is a generic class that takes in
    the input type and the output type of the component.

    It is responsible for:
        1. Initializing the component
        2. Initializing the upstream components
    """

    def __init__(
        self,
        *upstreams: Component,
        name: Optional[str] = None,
    ) -> None:
        self._name = name or self.__class__.__name__
        self._id = uuid4()
        self.upstreams: Dict[str, Component] = {
            upstream.name: upstream for upstream in upstreams
        }
        self._status: ComponentStatus = ComponentStatus.created

        self.initialized_event = asyncio.Event()
        self.initialized_components: Set[Component] = set()

    def __repr__(self) -> str:
        return f"<name={self._name}, component_id={self._id} status={self._status}>"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Component) and self._id == other._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> ComponentStatus:
        return self._status

    @status.setter
    def status(self, value: ComponentStatus) -> None:
        self._status = value

    async def initialize(self) -> None:
        """
        This is the place where you can do some initialization work for your component

        As an example, you can initialize a model here or load a file,
        which is needed for your component to work
        """
        return None

    async def initialize_wrapper(self) -> None:
        """
        Extend this method if your component has some work that needs to be done on server startup

        This is a great place to initialize libraries to access external libraries, warm up models, etc

        This runs after all objects have been constructed
        """
        try:
            uninitialized_components = [
                component
                for component in self.upstreams.values()
                if component not in self.initialized_components
            ]
            await asyncio.gather(
                *[
                    component.initialize_wrapper()
                    for component in uninitialized_components
                ],
                # This forces an error to be propagated up if any of the async tasks throw exceptions
                return_exceptions=False,
            )

            for component in uninitialized_components:
                self.initialized_components.add(component)
        except Exception as e:
            logger.error("Encountered issue initializing components", e)
            raise e

        self.initialized_event.set()
        self.status = ComponentStatus.initialized

        await self.initialize()

    # User Interfaces below
    async def execute(self, input: INPUT_TYPE, **kwargs) -> OUTPUT_TYPE:
        """
        The actual meat of the component.
        Custom component has to implement

        If your component has to complex input data structure, make sure to override this method in order to
            construct your input data with upstream components' output data

        upstream_outputs contains data that was parsed by upstreams
        """
        raise NotImplementedError(
            "execute function needs to be implemented by component",
        )

    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        """
        This function defines which features are required for this component to work

        Our system will automatically fetch the required features from the feature store
            to make this model evaluation possible
        """
        return set()

    def get_feature(
        self,
        identifier: Identifier,
        feature_name: str,
    ) -> WyvernFeature:
        """
        This function gets the feature value for the given identifier
        The features are cached once fetched/evaluated.

        The feature that lives in the feature store should be
          just using the feature name without the "feature_view:" prefix
          For example, if your you have a feature view "fv" and a feature "wyvern_feature",
            then you would have defined "fv:wyvern_feature" in manifest_feature_names.
            However, when you fetch the feature value with this function,
            you just have to pass in feature_name="wyvern_feature".
        """
        current_request = request_context.ensure_current_request()
        feature_data = current_request.feature_map.feature_map.get(identifier)
        if not feature_data:
            return None
        return feature_data.features.get(feature_name)

    def get_all_features(
        self,
        identifier: Identifier,
    ) -> Dict[str, WyvernFeature]:
        """
        This function gets all features for the given identifier
        The features are cached once fetched/evaluated.
        """
        current_request = request_context.ensure_current_request()
        feature_data = current_request.feature_map.feature_map.get(identifier)
        if not feature_data:
            return {}
        return feature_data.features
