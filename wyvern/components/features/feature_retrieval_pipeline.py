# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Generic, List, Optional, Set, Type

from ddtrace import tracer
from pydantic.generics import GenericModel

from wyvern.components.component import Component
from wyvern.components.features.feature_logger import (
    FeatureEventLoggingComponent,
    FeatureEventLoggingRequest,
)
from wyvern.components.features.feature_store import (
    FeatureStoreRetrievalComponent,
    FeatureStoreRetrievalRequest,
    feature_store_retrieval_component,
)
from wyvern.components.features.realtime_features_component import (
    RealtimeFeatureComponent,
    RealtimeFeatureRequest,
)
from wyvern.entities.candidate_entities import CandidateSetEntity
from wyvern.entities.feature_entities import FeatureData, FeatureMap
from wyvern.entities.feature_entity_helpers import feature_map_create, feature_map_join
from wyvern.entities.identifier_entities import WyvernEntity
from wyvern.wyvern_typing import REQUEST_ENTITY

logger = logging.getLogger(__name__)


class FeatureRetrievalPipelineRequest(GenericModel, Generic[REQUEST_ENTITY]):
    """
    This is the input to the FeatureRetrievalPipeline component that is used to retrieve features.

    Attributes:
        request: The request that is used to retrieve features. This is used to retrieve the entities and
            identifiers that are needed to compute the features.
        requested_feature_names: The feature names that are
            requested. This is used to filter out the real-time features that are calculated instead of
            retrieved from the feature store. ie: `product_fv:FEATURE_PRODUCT_AMOUNT_PAID_LAST_15_DAYS`
        feature_overrides: This is used to override the default real-time features.
    """

    request: REQUEST_ENTITY
    requested_feature_names: Set[str]
    feature_overrides: Set[Type[RealtimeFeatureComponent]] = set()


class FeatureRetrievalPipeline(
    Component[FeatureRetrievalPipelineRequest[REQUEST_ENTITY], FeatureMap],
    Generic[REQUEST_ENTITY],
):
    """
    This component is used to retrieve features for a given request. It is composed of the following components:
        1. FeatureStoreRetrievalComponent: This component is used to retrieve features from the feature store.
        2. RealtimeFeatureComponent: This component is used to compute real-time features.
        3. FeatureEventLoggingComponent: This component is used to log feature events.

    """

    def __init__(
        self,
        *upstreams: Component,
        name: str,
        handle_exceptions: bool = False,
    ):
        """
        Args:
            *upstreams: The upstream components to this component.
            name: The name of this component.
            handle_exceptions: Whether to handle feature store exceptions. Defaults to False.
                If True, missing feature values will be None instead of raising exceptions.
                If False, exceptions will be raised.
        """
        self.real_time_features: List[
            RealtimeFeatureComponent
        ] = RealtimeFeatureComponent.real_time_features
        self.feature_retrieval_component: FeatureStoreRetrievalComponent = (
            feature_store_retrieval_component
        )
        self.feature_logger_component: FeatureEventLoggingComponent = (
            FeatureEventLoggingComponent()
        )
        self.handle_exceptions = handle_exceptions
        super().__init__(
            feature_store_retrieval_component,
            self.feature_logger_component,
            *self.real_time_features,
            *upstreams,
            name=name,
        )

    @tracer.wrap(name="FeatureRetrievalPipeline._generate_real_time_features")
    def _generate_real_time_features(
        self,
        input: FeatureRetrievalPipelineRequest[REQUEST_ENTITY],
    ) -> List[RealtimeFeatureComponent]:
        """
        Flatten all the real-time feature names into one list for the request/input
        """
        return [
            real_time_feature
            for real_time_feature in self.real_time_features
            if type(real_time_feature) in input.feature_overrides
            or real_time_feature.output_feature_names.intersection(
                input.requested_feature_names,
            )
        ]

    @tracer.wrap(name="FeatureRetrievalPipeline.execute")
    async def execute(
        self, input: FeatureRetrievalPipelineRequest[REQUEST_ENTITY], **kwargs
    ) -> FeatureMap:
        """
        This method is used to retrieve features for a given request.

        It is composed of the following steps:
            0. Figure out which features are real-time features and which features are feature store features.
            1. Retrieve features from the feature store.
            2. Compute real-time features.
            3. Combine the feature store features and real-time features into one FeatureMap.
            4. Log the feature values to the feature event logging component.
        """
        # Only evaluate real-time features where the output feature names are in the requested feature names
        # Or the client wants to evaluate the feature
        # TODO (suchintan): We don't support "chained" real-time features yet.. hopefully soon
        real_time_features = self._generate_real_time_features(input)

        # Figure out which features are real-time features based on the definitions within the real-time feature object
        features_requested_by_real_time_features = {
            feature_name
            for real_time_feature in real_time_features
            for feature_name in real_time_feature.output_feature_names
        }

        # Figure out which features come from the feature store
        feature_names_to_retrieve_from_feature_store = (
            input.requested_feature_names.difference(
                features_requested_by_real_time_features,
            )
        )

        all_entities = input.request.get_all_entities(cached=True)
        all_identifiers = input.request.get_all_identifiers(cached=True)
        # TODO (suchintan): Pass in the feature retrieval features here so they can leverage them
        feature_retrieval_request = FeatureStoreRetrievalRequest(
            identifiers=all_identifiers,
            feature_names=list(feature_names_to_retrieve_from_feature_store),
        )

        feature_retrieval_response: FeatureMap = (
            await self.feature_retrieval_component.execute(
                input=feature_retrieval_request,
                handle_exceptions=self.handle_exceptions,
                **kwargs,
            )
        )

        """
        TODO (suchintan):
        1. Figure out a set of: (Candidate entities), (Non-candidate entities), (Request)
        2. Evaluate real-time features for each of the above
        3. Find the cross-section of all candidate entities and non-candidate entities
        4. Evaluate candidate features for the cross-section
        5. Combine all of the feature results together into one FeatureMap
        """

        # TODO (suchintan): Improve performance by using iterutils instead of list comprehensions
        # TODO (suchintan): Figure out a better pattern for CompositeIdentifierType
        #   it should enforce order automatically instead of blowing up
        with tracer.trace("FeatureRetrievalPipeline.generate_entities"):
            candidate_entities: List[WyvernEntity] = []
            request_entities = all_entities
            if isinstance(input.request, CandidateSetEntity):
                """
                This branch partitions the `all_entities` list into two lists:
                    1. Candidate_entities (ie Product and Brand) -- the things we will be ranking
                    2. Request_entities (ie User and Query) --
                        The things that are the same across all items being ranked
                """

                # TODO (shu): assume two products have the same brand:
                # here we will have duplicated brands. Is it okay to have duplicated brands in candidate_entities?
                # might need to dedupe
                candidate_entities = [
                    entity
                    for candidate in input.request.candidates
                    for entity in candidate.get_all_entities()
                ]

                candidate_identifiers = {
                    candidate.identifier for candidate in candidate_entities
                }
                request_entities = [
                    entity
                    for entity in all_entities
                    if entity.identifier not in candidate_identifiers
                ]

        with tracer.trace("FeatureRetrievalPipeline.real_time_no_entity_features"):
            request = RealtimeFeatureRequest[REQUEST_ENTITY](
                request=input.request,
                feature_retrieval_response=feature_retrieval_response,
            )
            real_time_request_no_entity_features: List[
                Optional[FeatureData]
            ] = await asyncio.gather(
                *[
                    real_time_feature.compute_request_features_wrapper(
                        request=request,
                    )
                    for real_time_feature in real_time_features
                    if real_time_feature.can_execute_on(request.request, None, None)
                ]
            )

        with tracer.trace("FeatureRetrievalPipeline.real_time_entity_features"):
            real_time_request_features: List[
                Optional[FeatureData]
            ] = await asyncio.gather(
                *[
                    real_time_feature.compute_features_wrapper(
                        request=request,
                        entity=entity,
                    )
                    for real_time_feature in real_time_features
                    for entity in request_entities
                    if real_time_feature.can_execute_on(request.request, entity, None)
                ]
            )

        with tracer.trace("FeatureRetrievalPipeline.real_time_combination_features"):
            real_time_request_combination_features: List[
                Optional[FeatureData]
            ] = await asyncio.gather(
                *[
                    real_time_feature.compute_composite_features_wrapper(
                        primary_entity=entity,
                        secondary_entity=secondary_entity,
                        request=request,
                    )
                    for real_time_feature in real_time_features
                    for entity in request_entities
                    for secondary_entity in request_entities
                    if entity != secondary_entity
                    and real_time_feature.can_execute_on(
                        request.request,
                        entity,
                        secondary_entity,
                    )
                ]
            )

        real_time_candidate_features: List[Optional[FeatureData]] = []
        real_time_candidate_combination_features: List[Optional[FeatureData]] = []

        if isinstance(input.request, CandidateSetEntity):
            with tracer.trace("FeatureRetrievalPipeline.real_time_candidate_features"):
                real_time_candidate_features = await asyncio.gather(
                    *[
                        real_time_feature.compute_features_wrapper(
                            entity=entity,
                            request=request,
                        )
                        for real_time_feature in real_time_features
                        for entity in candidate_entities
                        if real_time_feature.can_execute_on(
                            request.request,
                            entity,
                            None,
                        )
                    ]
                )

            with tracer.trace(
                "FeatureRetrievalPipeline.real_time_candidate_combination_features",
            ):
                real_time_candidate_combination_features = await asyncio.gather(
                    *[
                        real_time_feature.compute_composite_features_wrapper(
                            primary_entity=entity,
                            secondary_entity=secondary_entity,
                            request=request,
                        )
                        for real_time_feature in real_time_features
                        for entity in candidate_entities
                        for secondary_entity in request_entities
                        if real_time_feature.can_execute_on(
                            request.request,
                            entity,
                            secondary_entity,
                        )
                    ]
                )

        # TODO (kerem): Group feature views together at execution time so there never is a chance of collision
        # Idea 1: No two feature views can have the feature definitions
        # Idea 2: Define feature views that have the same interface,
        #   and we collect them together ahead of this dict comprehension
        # pytest / linter validation: we should assert for feature name conflicts -- this should never happen
        with tracer.trace("FeatureRetrievalPipeline.create_feature_map"):
            real_time_feature_responses = feature_map_create(
                *real_time_request_no_entity_features,
                *real_time_request_features,
                *real_time_request_combination_features,
                *real_time_candidate_features,
                *real_time_candidate_combination_features,
            )

        with tracer.trace("FeatureRetrievalPipeline.create_feature_response"):
            await self.feature_logger_component.execute(
                FeatureEventLoggingRequest(
                    request=input.request,
                    feature_map=real_time_feature_responses,
                ),
            )
            # TODO (suchintan): Improve performance of this
            feature_responses = feature_map_join(
                feature_retrieval_response,
                real_time_feature_responses,
            )

        return feature_responses
