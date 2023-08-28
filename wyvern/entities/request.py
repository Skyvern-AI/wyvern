# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import PrivateAttr

from wyvern.entities.identifier import Identifier
from wyvern.entities.identifier_entities import WyvernDataModel


class BaseWyvernRequest(WyvernDataModel):
    """
    Base class for all Wyvern requests. This class is used to generate an identifier for the request.

    Attributes:
        request_id: The request id.
        include_events: Whether to include events in the response.
    """

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
        """
        Generates an identifier for the request.

        Returns:
            Identifier: The identifier for the request. The identifier type is "request".
        """
        return Identifier(
            identifier=self.request_id,
            identifier_type="request",
        )
