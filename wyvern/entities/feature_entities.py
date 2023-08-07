# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict

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
