# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Optional

import polars as pl
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


class FeatureMapPolars:
    """
    A class to represent a map of identifiers to feature data. Uses polars library for efficient data processing.
    """

    feature_map: Dict[str, pl.DataFrame] = {}

    def __init__(self, feature_map: Optional[FeatureMap] = None, **kwargs):
        if feature_map is None:
            self.feature_map = {}
        else:
            data: Dict[str, List[List[WyvernFeature]]] = {}
            columns = {}
            for identifier, feature_data in feature_map.feature_map.items():
                if identifier.identifier_type not in data:
                    data[identifier.identifier_type] = []
                    columns[identifier.identifier_type] = list(
                        feature_data.features.keys(),
                    )
                data[identifier.identifier_type].append(
                    [identifier.identifier] + list(feature_data.features.values()),
                )

            result = {}
            for identifier_type, identifier_data in data.items():
                column_list = ["identifier"]
                column_list.extend(columns[identifier_type])
                column_list = [col.replace(":", "__") for col in column_list]
                result[identifier_type] = pl.DataFrame(
                    identifier_data,
                    schema=column_list,
                )
            self.feature_map = result

    def get_features(
        self,
        identifier_type: str,
        identifier_list: List[str],
        feature_names: List[str],
    ) -> pl.DataFrame:
        df = self.feature_map[identifier_type]
        # Filter the dataframe by both identifier_type and identifier
        df = df.filter(pl.col("identifier").is_in(identifier_list))

        # Process feature names, adding identifier to the selection
        feature_names = ["identifier"] + [f.replace(":", "__") for f in feature_names]
        existing_cols = df.columns
        for col_name in feature_names:
            if col_name not in existing_cols:
                # Add a new column filled with None values if it doesn't exist
                df = df.with_columns(pl.lit(None).alias(col_name))
        df = df.select(feature_names)

        return df


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
