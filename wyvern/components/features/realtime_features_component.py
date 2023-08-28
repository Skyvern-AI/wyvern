# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    get_args,
)

from pydantic.generics import GenericModel

from wyvern.components.component import Component
from wyvern.entities.feature_entities import FeatureData, FeatureMap
from wyvern.entities.identifier_entities import WyvernEntity
from wyvern.feature_store.constants import (
    FULL_FEATURE_NAME_SEPARATOR,
    SQL_COLUMN_SEPARATOR,
)
from wyvern.wyvern_typing import REQUEST_ENTITY

logger = logging.getLogger(__name__)

PRIMARY_ENTITY = TypeVar("PRIMARY_ENTITY", bound=WyvernEntity)
"""
The primary entity is the entity that is the main entity for the feature. For example, if we are computing
the feature for a user, the primary entity would be the user.
"""
SECONDARY_ENTITY = TypeVar("SECONDARY_ENTITY", bound=WyvernEntity)
"""
The secondary entity is the entity that is the secondary entity for the feature. For example, if we are computing
the feature for a user and a product, the secondary entity would be the product. If we are computing the feature
for a user, the secondary entity would be None.
"""


class RealtimeFeatureRequest(GenericModel, Generic[REQUEST_ENTITY]):
    """
    This is the request that is passed into the realtime feature component.
    """

    request: REQUEST_ENTITY
    feature_retrieval_response: FeatureMap


class RealtimeFeatureEntity(GenericModel, Generic[PRIMARY_ENTITY, SECONDARY_ENTITY]):
    """
    This is the entity that is passed into the realtime feature component. It contains the primary entity and
    the secondary entity. If the feature is only for the primary entity, the secondary entity will be None.
    """

    # Can pass in multiple WYVERN_ENTITIES here as well
    primary_entity: Optional[PRIMARY_ENTITY]
    secondary_entity: Optional[SECONDARY_ENTITY]


class RealtimeFeatureComponent(
    Component[
        Tuple[
            RealtimeFeatureRequest[REQUEST_ENTITY],
            RealtimeFeatureEntity[PRIMARY_ENTITY, SECONDARY_ENTITY],
        ],
        Optional[FeatureData],
    ],
    Generic[PRIMARY_ENTITY, SECONDARY_ENTITY, REQUEST_ENTITY],
):
    """
    This is the base class for all realtime feature components. It contains the logic for computing the realtime
    feature. The realtime feature component can be used to compute features for a single entity, two entities, or
    a request. The realtime feature component can also be used to compute composite features for two entities.

    The realtime feature component is a generic class that takes in the primary entity, secondary entity, and request
    entity as type parameters. The primary entity is the entity that is the main entity for the feature. For example,
    if we are computing the feature for a user, the primary entity would be the user. The secondary entity is the
    entity that is the secondary entity for the feature. For example, if we are computing the feature for a user and
    a product, the secondary entity would be the product. If we are computing the feature for a user, the secondary
    entity would be None. The request entity is the request that is passed into the realtime feature component. We can
    use the request entity to compute features for a request. For example, if we are computing the realtime features for
    a ranking request, the request entity would be the ranking request. We can combine the primary entity, secondary
    entity, and request entity to compute composite features.

    Attributes:
        NAME: The name of the realtime feature component. This is used to identify the realtime feature component.
        real_time_features: A list of all the realtime feature components.
        component_registry: A dictionary that maps the name of the realtime feature component to the realtime feature
    """

    NAME: str = ""

    real_time_features: List[RealtimeFeatureComponent] = []
    component_registry: Dict[str, RealtimeFeatureComponent] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        """
        This is a great spot to define a registry for RealtimeFeatureComponent

        Problem: This doesn't handle upstream relationships at all,
            as the current upstream design requires a concrete instance

        Solution: Migrate the entire Component system to a registry pattern and overwrite the __new__ to return
            the instance from the registry

        Caveat: Upstream relationships, circular dependencies,
            and so on will have to be carefully managed with this registry
        """
        instance = cls()
        cls.real_time_features.append(instance)
        cls.component_registry[instance.name] = instance

    def __init__(
        self,
        *upstreams: Component,
        # TODO (suchintan) -> Refactor: Change to Type[Component]
        #  Then fetch component from registry during initialize instead of passing it in during __init__
        # TODO (suchintan): Eventually stop requiring these parameters
        output_feature_names: Optional[Set[str]] = None,
        required_feature_names: Optional[Set[str]] = None,
        name: Optional[str] = None,
    ):
        """
        :param name: Name of the component
        :param output_feature_names: features outputted by this real-time feature
        """
        name = name or self.NAME
        super().__init__(*upstreams, name=name)

        # TODO (suchintan): We should try to take advantage of
        #   https://stackoverflow.com/questions/73746553/access-type-argument-in-any-specific-subclass-of-user-defined-generict-class
        #   To understand what the underlying generic types really are
        self.primary_entity_type = self.get_type_args_simple(0)
        self.secondary_entity_type = self.get_type_args_simple(1)
        self.request_entity_type = self.get_type_args_simple(2)

        # TODO shu: refactor this tuple into using the entity_identifier_type instead of the class name
        self.entity_names: List[str] = []
        if self.primary_entity_type is not Any:
            self.entity_names.append(self.primary_entity_type.__name__.lower())
        if self.secondary_entity_type is not Any:
            self.entity_names.append(self.secondary_entity_type.__name__.lower())
        if len(self.entity_names) == 0:
            if self.request_entity_type is Any:
                raise ValueError(
                    f"RealtimeFeatureComponent {self.name} must have at least one entity type specified",
                )
            self.entity_names.append(self.request_entity_type.__name__.lower())

        self.entity_identifier_type = FULL_FEATURE_NAME_SEPARATOR.join(
            self.entity_names,
        )
        self.entity_identifier_type_column = SQL_COLUMN_SEPARATOR.join(
            self.entity_names,
        )

        self.required_feature_names: set[str] = required_feature_names or set()
        output_feature_names = output_feature_names or set()
        self.output_feature_names: set[str] = {
            f"{self.name}:{feature}" for feature in output_feature_names
        }

    @classmethod
    def get_type_args_simple(cls, index: int) -> Type:
        """
        Get the type argument at the given index for the class. This is used to get the primary entity type, secondary
        entity type, and request entity type.
        """
        return get_args(cls.__orig_bases__[0])[index]  # type: ignore

    @classmethod
    def get_entity_names(
        cls,
        full_feature_name: str,
    ) -> Optional[List[str]]:
        """
        Get the entity identifier type, which will be used as sql column name

        full_feature_name is of the form `<component_name>:<feature_name>`
        """
        split_feature = full_feature_name.split(FULL_FEATURE_NAME_SEPARATOR)
        if len(split_feature) != 2:
            logger.warning(
                f"Invalid feature name {full_feature_name} - more than one separator found",
            )
            return None

        component_name, _ = split_feature
        component = cls.component_registry.get(component_name)
        return component.entity_names if component else None

    @classmethod
    def get_entity_type_column(
        cls,
        full_feature_name: str,
    ) -> Optional[str]:
        """
        Get the entity identifier type, which will be used as sql column name

        full_feature_name is of the form `<component_name>:<feature_name>`
        """
        split_feature = full_feature_name.split(FULL_FEATURE_NAME_SEPARATOR)
        if len(split_feature) != 2:
            logger.warning(
                f"Invalid feature name {full_feature_name} - more than one separator found",
            )
            return None

        component_name, _ = split_feature
        component = cls.component_registry.get(component_name)
        return component.entity_identifier_type_column if component else None

    def can_execute_on(
        self,
        request: REQUEST_ENTITY,
        primary_entity: Optional[PRIMARY_ENTITY],
        secondary_entity: Optional[SECONDARY_ENTITY],
    ) -> bool:
        """
        Checks if the input matches the entity type, so we can execute on it
        """
        type_matches = True
        if self.primary_entity_type is not Any:
            type_matches = type_matches and isinstance(
                primary_entity,
                self.primary_entity_type,
            )
        elif primary_entity is not None:
            # primary entity should be none if primary_entity_type is Any
            type_matches = False

        if self.request_entity_type is not Any:
            type_matches = type_matches and isinstance(
                request,
                self.request_entity_type,
            )

        if self.secondary_entity_type is not Any:
            type_matches = type_matches and isinstance(
                secondary_entity,
                self.secondary_entity_type,
            )
        elif secondary_entity is not None:
            # secondary entity should be none if secondary_entity_type is Any
            type_matches = False

        return type_matches

    async def execute(
        self,
        input: Tuple[
            RealtimeFeatureRequest[REQUEST_ENTITY],
            RealtimeFeatureEntity[PRIMARY_ENTITY, SECONDARY_ENTITY],
        ],
        **kwargs,
    ) -> Optional[FeatureData]:
        # TODO (Suchintan): Delete this method -- this has been fully delegated upwards?
        request = input[0]
        entities = input[1]

        if not self.can_execute_on(
            request.request,
            entities.primary_entity,
            entities.secondary_entity,
        ):
            return None

        if (
            entities.secondary_entity is not None
            and entities.primary_entity is not None
        ):
            resp = await self.compute_composite_features(
                entities.primary_entity,
                entities.secondary_entity,
                request,
            )
            # TODO (suchintan): using this for debugging, remove later
            if resp is None:
                logger.info(
                    f"Failed to compute composite features for "
                    f"{self} {entities.primary_entity.identifier} {entities.secondary_entity.identifier}",
                )
            return resp

        if entities.primary_entity is not None:
            resp = await self.compute_features(
                entities.primary_entity,
                request,
            )
            # TODO (suchintan): using this for debugging, remove later
            if resp is None:
                logger.info(
                    f"Failed to compute features for "
                    f"{self} {entities.primary_entity.identifier}",
                )
            return resp

        # TODO (suchintan): Lowercase feature names?
        resp = await self.compute_request_features(request)

        # TODO (suchintan): using this for debugging, remove later
        if resp is None:
            logger.info(
                f"Failed to compute request features for {self} {request.request}",
            )
        return resp

    async def compute_request_features(
        self,
        request: RealtimeFeatureRequest[REQUEST_ENTITY],
    ) -> Optional[FeatureData]:
        return None

    async def compute_features(
        self,
        entity: PRIMARY_ENTITY,
        request: RealtimeFeatureRequest[REQUEST_ENTITY],
    ) -> Optional[FeatureData]:
        return None

    async def compute_composite_features(
        self,
        primary_entity: PRIMARY_ENTITY,
        secondary_entity: SECONDARY_ENTITY,
        request: RealtimeFeatureRequest[REQUEST_ENTITY],
    ) -> Optional[FeatureData]:
        return None

    async def compute_request_features_wrapper(
        self,
        request: RealtimeFeatureRequest[REQUEST_ENTITY],
    ) -> Optional[FeatureData]:
        feature_data = await self.compute_request_features(request)
        return self.set_full_feature_name(feature_data)

    async def compute_features_wrapper(
        self,
        entity: PRIMARY_ENTITY,
        request: RealtimeFeatureRequest[REQUEST_ENTITY],
    ) -> Optional[FeatureData]:
        feature_data = await self.compute_features(entity, request)
        return self.set_full_feature_name(feature_data)

    async def compute_composite_features_wrapper(
        self,
        primary_entity: PRIMARY_ENTITY,
        secondary_entity: SECONDARY_ENTITY,
        request: RealtimeFeatureRequest[REQUEST_ENTITY],
    ) -> Optional[FeatureData]:
        feature_data = await self.compute_composite_features(
            primary_entity,
            secondary_entity,
            request,
        )
        return self.set_full_feature_name(feature_data)

    def set_full_feature_name(
        self,
        feature_data: Optional[FeatureData],
    ) -> Optional[FeatureData]:
        """
        Sets the full feature name for the feature data
        """
        if not feature_data:
            return None

        return FeatureData(
            identifier=feature_data.identifier,
            features={
                f"{self.name}:{feature_name}": feature_value
                for feature_name, feature_value in feature_data.features.items()
            },
        )
