# -*- coding: utf-8 -*-
from enum import Enum

from pydantic import BaseModel


class SortEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class Sort(BaseModel):
    sort_key: str
    sort_field: str
    sort_order: SortEnum = SortEnum.desc
