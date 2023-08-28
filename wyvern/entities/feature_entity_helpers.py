# -*- coding: utf-8 -*-
from typing import Dict, Optional

from wyvern.entities.feature_entities import FeatureData, FeatureMap
from wyvern.entities.identifier import Identifier


def feature_map_join(*feature_maps: FeatureMap) -> FeatureMap:
    """
    Joins multiple feature maps into a single feature map. Used to join feature maps from different sources.
    """
    return feature_map_create(
        *[value for map in feature_maps for value in map.feature_map.values()]
    )


def feature_map_create(*feature_data: Optional[FeatureData]) -> FeatureMap:
    """
    Creates a feature map from a list of feature data. Used to create feature maps from different sources.
    """
    feature_map: Dict[Identifier, FeatureData] = {}
    for data in feature_data:
        if data is None:
            continue

        if data.identifier in feature_map:
            # print(f"Duplicate keys found in feature map {data}")
            # TODO (suchintan): handle duplicate keys at this stage
            feature_map[data.identifier].features.update(data.features)
        else:
            feature_map[data.identifier] = data

    return FeatureMap(feature_map=feature_map)
