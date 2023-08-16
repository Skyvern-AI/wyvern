# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List

from pydantic.main import BaseModel

from wyvern.entities.identifier import Identifier
from wyvern.wyvern_typing import WyvernFeature


class FeatureData(BaseModel, frozen=True):
    identifier: Identifier
    features: Dict[str, WyvernFeature] = {}

    def __str__(self) -> str:
        return f"identifier={self.identifier} features={self.features}"

    def __repr__(self):
        return self.__str__()


class FeatureMap(BaseModel, frozen=True):
    feature_map: Dict[Identifier, FeatureData]


def build_empty_feature_map(
    identifiers: List[Identifier],
    feature_names: List[str],
) -> FeatureMap:
    return FeatureMap(
        feature_map={
            identifier: FeatureData(
                identifier=identifier,
                features={feature: None for feature in feature_names},
            )
            for identifier in identifiers
        },
    )
