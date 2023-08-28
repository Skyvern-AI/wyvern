# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GetOnlineFeaturesRequest(BaseModel):
    """
    Request object for getting online features.

    Attributes:
        entities: A dictionary of entity name to entity value.
        features: A list of feature names.
        full_feature_names: A boolean indicating whether to return full feature names. If True, the feature names will
        be returned in the format `<feature_view_name>__<feature_name>`. If False, only the feature names will be
        returned.
    """

    entities: Dict[str, Any] = {}
    features: List[str] = []
    full_feature_names: bool = False


class GetHistoricalFeaturesRequest(BaseModel):
    """
    Request object for getting historical features.

    Attributes:
        entities: A dictionary of entity name to entity value.
        timestamps: A list of timestamps. Used to retrieve historical features at specific timestamps. If not provided,
            the latest feature values will be returned.
        features: A list of feature names.
    """

    entities: Dict[str, List[Any]]
    timestamps: List[datetime] = []
    features: List[str] = []


class GetFeastHistoricalFeaturesRequest(BaseModel):
    """
    Request object for getting historical features from Feast.

    Attributes:
        full_feature_names: A boolean indicating whether to return full feature names. If True, the feature names will
            be returned in the format `<feature_view_name>__<feature_name>`. If False, only the feature names will be
            returned.
        entities: A dictionary of entity name to entity value.
        features: A list of feature names.
    """

    full_feature_names: bool = False
    entities: Dict[str, List[Any]] = {}
    features: List[str] = []


class GetHistoricalFeaturesResponse(BaseModel):
    """
    Response object for getting historical features.

    Attributes:
        results: A list of dictionaries containing feature values.
    """

    results: List[Dict[str, Any]] = []


class MaterializeRequest(BaseModel):
    """
    Request object for materializing feature views.

    Attributes:
        end_date: The end date of the materialization window. Defaults to the current time.
        feature_views: A list of feature view names to materialize. If not provided, all feature views will be
            materialized.
        start_date: The start date of the materialization window. Defaults to None, which will use the start date of
            the feature view.
    """

    end_date: datetime = Field(default_factory=datetime.utcnow)
    feature_views: Optional[List[str]] = None
    start_date: Optional[datetime] = None


class RequestEntityIdentifierObjects(BaseModel):
    """
    Request object for getting entity identifier objects.

    Attributes:
        request_ids: A list of request IDs.
        entity_identifiers: A list of entity identifiers.
        feature_names: A list of feature names.
    """

    request_ids: List[str] = []
    entity_identifiers: List[str] = []
    feature_names: List[str] = []
