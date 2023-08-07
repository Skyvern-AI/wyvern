# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GetOnlineFeaturesRequest(BaseModel):
    entities: Dict[str, Any] = {}
    features: List[str] = []
    full_feature_names: bool = False


class GetHistoricalFeaturesRequest(BaseModel):
    entities: Dict[str, List[Any]]
    timestamps: List[datetime] = []
    features: List[str] = []


class GetFeastHistoricalFeaturesRequest(BaseModel):
    full_feature_names: bool = False
    entities: Dict[str, List[Any]] = {}
    features: List[str] = []


class GetHistoricalFeaturesResponse(BaseModel):
    results: List[Dict[str, Any]] = []


class MaterializeRequest(BaseModel):
    end_date: datetime = Field(default_factory=datetime.utcnow)
    feature_views: Optional[List[str]] = None
    start_date: Optional[datetime] = None


class RequestEntityIdentifierObjects(BaseModel):
    request_ids: List[str] = []
    entity_identifiers: List[str] = []
    feature_names: List[str] = []
