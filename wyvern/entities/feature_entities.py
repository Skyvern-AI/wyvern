# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List

from pydantic.main import BaseModel

from wyvern.entities.identifier import Identifier
from wyvern.wyvern_typing import WyvernFeature


class FeatureData(BaseModel, frozen=True):
    """
    A class to represent the features of an entity.

    Attributes:
        identifier: The identifier of the entity.
        features: A dictionary of feature names to feature values.
    """

    identifier: Identifier
    features: Dict[str, WyvernFeature] = {}

    def __str__(self) -> str:
        return f"identifier={self.identifier} features={self.features}"

    def __repr__(self):
        return self.__str__()


class FeatureMap(BaseModel, frozen=True):
    """
    A class to represent a map of identifiers to feature data.

    TODO (kerem): Fix the data duplication between this class and the FeatureData class. The identifier field in the
        FeatureData class is redundant.
    """

    feature_map: Dict[Identifier, FeatureData]


def build_empty_feature_map(
    identifiers: List[Identifier],
    feature_names: List[str],
) -> FeatureMap:
    """
    Builds an empty feature map with the given identifiers and feature names.
    """
    return FeatureMap(
        feature_map={
            identifier: FeatureData(
                identifier=identifier,
                features={feature: None for feature in feature_names},
            )
            for identifier in identifiers
        },
    )
