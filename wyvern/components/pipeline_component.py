# -*- coding: utf-8 -*-
from functools import cached_property
from typing import Optional, Set, Type

from wyvern import request_context
from wyvern.components.api_route_component import APIRouteComponent
from wyvern.components.component import Component
from wyvern.components.features.feature_retrieval_pipeline import (
    FeatureRetrievalPipeline,
    FeatureRetrievalPipelineRequest,
)
from wyvern.components.features.realtime_features_component import (
    RealtimeFeatureComponent,
)
from wyvern.wyvern_typing import REQUEST_ENTITY, RESPONSE_SCHEMA


class PipelineComponent(APIRouteComponent[REQUEST_ENTITY, RESPONSE_SCHEMA]):
    def __init__(self, *upstreams: Component, name: Optional[str] = None) -> None:
        # TODO Kerem: if upstreams has the FeatureRetrievalPipeline, then the code is broken
        self.feature_retrieval_pipeline = FeatureRetrievalPipeline[REQUEST_ENTITY](
            name=f"{self.__class__.__name__}-feature_retrieval",
        )
        self.feature_names: Set[str] = set()
        super().__init__(*upstreams, self.feature_retrieval_pipeline, name=name)

    @cached_property
    def realtime_features_overrides(self) -> Set[Type[RealtimeFeatureComponent]]:
        """
        This function defines the set of RealtimeFeatureComponents that generates features
        with non-deterministic feature names.
        For example, feature names like matched_query_brand.
        That feature is defined like matched_query_{input.query.matched_query}, so it can refer to 10 or 20 features
        """
        return set()

    async def initialize(self) -> None:
        # get all the feature names from all the upstream components
        for component in self.initialized_components:
            for feature_name in component.manifest_feature_names:
                self.feature_names.add(feature_name)

    async def retrieve_features(self, request: REQUEST_ENTITY) -> None:
        """
        TODO shu: it doesn't support feature overrides. Write code to support that
        """
        feature_request = FeatureRetrievalPipelineRequest[REQUEST_ENTITY](
            request=request,
            requested_feature_names=self.feature_names,
            feature_overrides=self.realtime_features_overrides,
        )
        feature_map = await self.feature_retrieval_pipeline.execute(
            feature_request,
        )
        current_request = request_context.ensure_current_request()
        current_request.feature_map = feature_map

    async def warm_up(self, input: REQUEST_ENTITY) -> None:
        await super().warm_up(input)

        # TODO shu: split feature_retrieval_pipeline into
        # 1. feature retrieval from feature store 2. realtime feature computation
        # then the warm_up and feature retrieval from feature store can be done in parallel
        # suchintan: we also need to retrieve brand features from the feature store
        # and brand info would only be available via hydration so hydration has to be done first
        await self.retrieve_features(input)
