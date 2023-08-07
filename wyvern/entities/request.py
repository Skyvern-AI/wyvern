# -*- coding: utf-8 -*-
from typing import Optional

from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import WyvernDataModel


class BaseWyvernRequest(WyvernDataModel):
    request_id: str
    include_events: Optional[bool] = False

    @property
    def identifier(self) -> Identifier:
        return Identifier(
            identifier=self.request_id,
            identifier_type="request",
        )
