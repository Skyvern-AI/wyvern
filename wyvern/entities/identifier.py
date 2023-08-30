# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from enum import Enum
from typing import Union

from pydantic.main import BaseModel

from wyvern.config import settings
from wyvern.utils import generate_index_key

COMPOSITE_SEPARATOR = ":"
logger = logging.getLogger(__name__)


class SimpleIdentifierType(str, Enum):
    """
    Simple identifier types are those that are not composite.
    """

    PRODUCT = "product"
    QUERY = "query"
    BRAND = "brand"
    CATEGORY = "category"
    USER = "user"
    REQUEST = "request"


def composite(
    primary_identifier_type: SimpleIdentifierType,
    secondary_identifier_type: SimpleIdentifierType,
) -> str:
    """
    Composite identifier types are those that are composite. For example, a product with id p_1234 and type "product"
    a user with id u_1234 and type "user" would have a composite identifier of "p_1234:u_1234", and a composite
    identifier_type of "product:user". This is useful for indexing and searching for composite entities.
    """
    return f"{primary_identifier_type.value}{COMPOSITE_SEPARATOR}{secondary_identifier_type.value}"


class CompositeIdentifierType(str, Enum):
    """
    Composite identifier types are those that are composite. For example, a composite identifier type of
    "product:user" would be a composite identifier type for a product and a user. This is useful for indexing and
    searching for composite entities.
    """

    PRODUCT_QUERY = composite(
        SimpleIdentifierType.PRODUCT,
        SimpleIdentifierType.QUERY,
    )
    BRAND_QUERY = composite(SimpleIdentifierType.BRAND, SimpleIdentifierType.QUERY)
    CATEGORY_QUERY = composite(
        SimpleIdentifierType.CATEGORY,
        SimpleIdentifierType.QUERY,
    )
    USER_PRODUCT = composite(SimpleIdentifierType.PRODUCT, SimpleIdentifierType.USER)
    USER_BRAND = composite(SimpleIdentifierType.BRAND, SimpleIdentifierType.USER)
    USER_CATEGORY = composite(SimpleIdentifierType.CATEGORY, SimpleIdentifierType.USER)
    QUERY_USER = composite(SimpleIdentifierType.QUERY, SimpleIdentifierType.USER)


IdentifierType = Union[SimpleIdentifierType, CompositeIdentifierType]


class Identifier(BaseModel):
    """
    Identifiers exist to represent a unique entity through their unique id and their type
    For example: a product with id p_1234 and type "product" or a user with id u_1234 and type "user"

    Composite identifiers are also possible, for example:
        a product with id p_1234 and type "product"
        a user with id u_1234 and type "user"

        The composite identifier would be "p_1234:u_1234",
            and the composite identifier_type would be "product:user"
    """

    identifier: str
    identifier_type: str

    class Config:
        frozen = True

    def __str__(self) -> str:
        return f"{self.identifier_type}::{self.identifier}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    @staticmethod
    def as_identifier_type(
        identifier_type_string: str,
    ) -> IdentifierType:
        try:
            return SimpleIdentifierType(identifier_type_string)
        except ValueError:
            pass
        return CompositeIdentifierType(identifier_type_string)

    def index_key(self) -> str:
        return generate_index_key(
            settings.PROJECT_NAME,
            self.identifier_type,
            self.identifier,
        )


class CompositeIdentifier(Identifier):
    """
    Composite identifiers exist to represent a unique entity through their unique id and their type. At most, they
    can have two identifiers and two identifier types. For example:
        a product with id p_1234 and type "product"
        a user with id u_1234 and type "user"

        The composite identifier would be "p_1234:u_1234", and the composite identifier_type would be "product:user".
    """

    primary_identifier: Identifier
    secondary_identifier: Identifier

    def __init__(
        self, primary_identifier: Identifier, secondary_identifier: Identifier, **kwargs
    ):
        identifier = f"{primary_identifier.identifier}{COMPOSITE_SEPARATOR}{secondary_identifier.identifier}"
        identifier_type = self.as_identifier_type(
            primary_identifier.identifier_type
            + COMPOSITE_SEPARATOR
            + secondary_identifier.identifier_type,
        )
        super().__init__(
            identifier=identifier,
            identifier_type=identifier_type.value,
            primary_identifier=primary_identifier,
            secondary_identifier=secondary_identifier,
            **kwargs,
        )
