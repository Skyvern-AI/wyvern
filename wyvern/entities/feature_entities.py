# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Dict, List

import polars as pl
from pydantic.main import BaseModel

from wyvern.entities.identifier import Identifier, get_identifier_key
from wyvern.wyvern_typing import WyvernFeature

logger = logging.getLogger(__name__)

IDENTIFIER = "IDENTIFIER"


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


class FeatureDataFrame(BaseModel):
    """
    A class to store features in a polars dataframe.
    """

    df: pl.DataFrame = pl.DataFrame().with_columns(
        pl.Series(name=IDENTIFIER, dtype=pl.Utf8),
    )

    class Config:
        arbitrary_types_allowed = True
        frozen = True

    def get_features(
        self,
        identifiers: List[Identifier],
        feature_names: List[str],
    ) -> pl.DataFrame:
        # Filter the dataframe by identifier. If the identifier is a composite identifier, use the primary identifier
        identifier_keys = [get_identifier_key(identifier) for identifier in identifiers]
        return self.get_features_by_identifier_keys(
            identifier_keys=identifier_keys,
            feature_names=feature_names,
        )

    def get_features_by_identifier_keys(
        self,
        identifier_keys: List[str],
        feature_names: List[str],
    ) -> pl.DataFrame:
        # Filter the dataframe by identifier
        df = self.df.filter(pl.col(IDENTIFIER).is_in(identifier_keys))

        # Process feature names, adding identifier to the selection
        feature_names = [IDENTIFIER] + feature_names
        existing_cols = df.columns
        for col_name in feature_names:
            if col_name not in existing_cols:
                # Add a new column filled with None values if it doesn't exist
                df = df.with_columns(pl.lit(None).alias(col_name))
        df = df.select(feature_names)

        return df

    def get_all_features_for_identifier(self, identifier: Identifier) -> pl.DataFrame:
        identifier_key = get_identifier_key(identifier)
        return self.df.filter(pl.col(IDENTIFIER) == identifier_key)

    @staticmethod
    def build_empty_df(
        identifiers: List[Identifier],
        feature_names: List[str],
    ) -> FeatureDataFrame:
        """
        Builds an empty polars df with the given identifiers and feature names.
        """
        identifier_keys = [get_identifier_key(identifier) for identifier in identifiers]
        df_columns = [
            pl.Series(name=IDENTIFIER, values=identifier_keys, dtype=pl.Object),
        ]
        df_columns.extend(
            [pl.lit(None).alias(feature_name) for feature_name in feature_names],  # type: ignore
        )
        return FeatureDataFrame(df=pl.DataFrame().with_columns(df_columns))
