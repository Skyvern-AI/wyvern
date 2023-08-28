# -*- coding: utf-8 -*-
from typing import List, TypeVar, Union

from pydantic import BaseModel

from wyvern.entities.identifier_entities import WyvernEntity
from wyvern.entities.request import BaseWyvernRequest

T = TypeVar("T")
REQUEST_ENTITY = TypeVar("REQUEST_ENTITY", bound=BaseWyvernRequest)
WYVERN_ENTITY = TypeVar("WYVERN_ENTITY", bound=WyvernEntity)
GENERALIZED_WYVERN_ENTITY = TypeVar(
    "GENERALIZED_WYVERN_ENTITY",
    bound=Union[WyvernEntity, BaseWyvernRequest],
)
INPUT_TYPE = TypeVar("INPUT_TYPE")
OUTPUT_TYPE = TypeVar("OUTPUT_TYPE")
UPSTREAM_INPUT_TYPE = TypeVar("UPSTREAM_INPUT_TYPE")
UPSTREAM_OUTPUT_TYPE = TypeVar("UPSTREAM_OUTPUT_TYPE")
REQUEST_SCHEMA = TypeVar("REQUEST_SCHEMA", bound=BaseModel)
RESPONSE_SCHEMA = TypeVar("RESPONSE_SCHEMA", bound=BaseModel)

WyvernFeature = Union[float, str, List[float], None]
"""A WyvernFeature defines the type of a feature in Wyvern. It can be a float, a string, a list of floats, or None."""
