# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import PrivateAttr

from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import WyvernDataModel


class BaseWyvernRequest(WyvernDataModel):
    request_id: str
    include_events: Optional[bool] = False

    _identifier: Identifier = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._identifier = self.generate_identifier()

    @property
    def identifier(self) -> Identifier:
        return self._identifier

    def generate_identifier(self) -> Identifier:
        return Identifier(
            identifier=self.request_id,
            identifier_type="request",
        )
