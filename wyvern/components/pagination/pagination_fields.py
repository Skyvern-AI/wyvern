# -*- coding: utf-8 -*-
from pydantic import BaseModel


class PaginationFields(BaseModel):
    """
    Pagination fields for requests. This is a mixin class that can be used in any request that requires pagination.

    Attributes:
        user_page_size: Zero-indexed user facing page number
        user_page: Number of items per user facing page
        candidate_page_size: This is the size of the candidate page.
        candidate_page: This is the zero-indexed page number for the candidate set
    """

    user_page_size: int
    user_page: int
    candidate_page_size: int
    candidate_page: int
