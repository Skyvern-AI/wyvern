# -*- coding: utf-8 -*-
from enum import Enum

from pydantic import BaseModel


class SortEnum(str, Enum):
    """
    Enum for sort order.
    """

    asc = "asc"
    desc = "desc"


class Sort(BaseModel):
    """
    Sort class for sorting the results.

    Attributes:
        sort_key: The key to sort on.
        sort_field: The field to sort on.
        sort_order: The order to sort on. Defaults to desc.
    """

    sort_key: str
    sort_field: str
    sort_order: SortEnum = SortEnum.desc
