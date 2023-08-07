# -*- coding: utf-8 -*-
from pydantic import BaseModel


class PaginationFields(BaseModel):
    user_page_size: int
    user_page: int
    candidate_page_size: int
    candidate_page: int
