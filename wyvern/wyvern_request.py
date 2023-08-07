# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import fastapi
from pydantic import BaseModel

from wyvern.components.events.events import LoggedEvent
from wyvern.entities.feature_entities import FeatureMap


@dataclass
class WyvernRequest:
    method: str
    url: str
    url_path: str
    json: BaseModel
    headers: Dict[Any, Any]

    entity_store: Dict[str, Optional[Dict[str, Any]]]
    # TODO (suchintan): Validate that there is no thread leakage here
    # The list of list here is a minor performance optimization to prevent copying of lists for events
    events: List[Callable[[], List[LoggedEvent[Any]]]]

    feature_map: FeatureMap

    request_id: Optional[str] = None

    # TODO: params

    @classmethod
    def parse_fastapi_request(
        cls,
        json: BaseModel,
        req: fastapi.Request,
        request_id: Optional[str] = None,
    ) -> WyvernRequest:
        return cls(
            method=req.method,
            url=str(req.url),
            url_path=urlparse(str(req.url)).path,
            json=json,
            headers=dict(req.headers),
            entity_store={},
            events=[],
            feature_map=FeatureMap(feature_map={}),
            request_id=request_id,
        )
