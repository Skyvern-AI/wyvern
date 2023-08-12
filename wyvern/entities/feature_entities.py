# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, Generic

from pydantic.generics import GenericModel

from wyvern.entities.identifier import Identifier
from wyvern.wyvern_typing import T, WyvernFeature


class FeatureData(
    GenericModel,
    Generic[T],
):
    identifier: Identifier
    features: Dict[str, T] = {}

    def __str__(self) -> str:
        return f"identifier={self.identifier} features={self.features}"

    def __repr__(self):
        return self.__str__()

    class Config:
        frozen = True


class FeatureMap(GenericModel, Generic[T]):
    feature_map: Dict[Identifier, FeatureData[T]] = {}

    class Config:
        frozen = True


WyvernFeatureData = FeatureData[WyvernFeature]
