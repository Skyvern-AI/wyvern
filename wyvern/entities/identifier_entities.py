# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, PrivateAttr

from wyvern.entities.identifier import Identifier, SimpleIdentifierType


class WyvernDataModel(BaseModel):
    """
    WyvernDataModel is a base class for all data models that could be hydrated from Wyvern Index.

    Attributes:
        _all_entities: a list of all the entities under the tree
        _all_identifiers: a list of all the identifiers under the tree
    """

    _all_entities: Optional[List[WyvernEntity]] = PrivateAttr()
    _all_identifiers: Optional[List[Identifier]] = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # for performance purpose, we're caching all the entities and identifiers
        self._all_entities = None
        self._all_identifiers = None

    def index_fields(self) -> List[str]:
        """
        This method returns a list of fields that contains indexable data
        """
        return []

    # TODO (suchintan): Should we turn this into a `@property`?
    def get_all_entities(self, cached: bool = True) -> List[WyvernEntity]:
        """
        This method returns all of the entities associated with subclasses of this

        If cached is True, all the nodes under the tree will be cached
        """
        if cached and self._all_entities is not None:
            return self._all_entities

        # TODO (suchintan): Autogenerate composite identifiers here if possible
        # TODO (suchintan): Convert this to a property without causing issues lol
        # DFS to get all identifiers so that each entity could cache its own results
        all_entities: List[WyvernEntity] = []
        all_identifiers: List[Identifier] = []
        all_identifiers_set: Set[Identifier] = set()

        if isinstance(self, WyvernEntity):
            all_entities.append(self)
            all_identifiers.append(self.identifier)
            all_identifiers_set.add(self.identifier)

        for field in self.__fields__:
            value = getattr(self, field)
            if isinstance(value, WyvernDataModel):
                self._handle_value(
                    value,
                    all_entities,
                    all_identifiers,
                    all_identifiers_set,
                    cached,
                )
            elif isinstance(value, list):
                for item in value:
                    if not isinstance(item, WyvernDataModel):
                        continue
                    self._handle_value(
                        item,
                        all_entities,
                        all_identifiers,
                        all_identifiers_set,
                        cached,
                    )
        if cached:
            self._all_entities = all_entities
            self._all_identifiers = all_identifiers
        else:
            # empty the cache
            self._all_entities = None
            self._all_identifiers = None
        return all_entities

    def _handle_value(
        self,
        value: WyvernDataModel,
        all_entities: List[WyvernEntity],
        all_identifiers: List[Identifier],
        all_identifiers_set: Set[Identifier],
        cached: bool,
    ) -> None:
        field_entities = value.get_all_entities(cached=cached)
        for field_entity in field_entities:
            if field_entity.identifier in all_identifiers_set:
                continue
            all_identifiers_set.add(field_entity.identifier)
            all_identifiers.append(field_entity.identifier)
            all_entities.append(field_entity)

    # TODO (suchintan): Should we turn this into a `@property`?
    def get_all_identifiers(self, cached: bool = True) -> List[Identifier]:
        """
        This method generally returns all of the identifiers associated with subclasses of this

        Example: You create a QueryProductEntity with query="test" and product_id="1234"
            It subclasses QueryEntity and ProductEntity, which both have an identifier
            This method will return a list of both of those identifiers

        Example: You create a ProductSearchRankingRequest with
            query="test", candidates=["1234", ...], user="u_1234"
            This method will return the user and query identifier
            It will also return the identifiers for each candidate (thanks to the implementation in CandidateEntity)

        Note: While this checks for `WyvernEntity` -- a `WyvernDataModel` can have many
            entities within it, it itself may not be an entity
        """

        if cached:
            if self._all_identifiers is None:
                self.get_all_entities(cached=cached)
            return self._all_identifiers or []
        else:
            return [
                entity.identifier for entity in self.get_all_entities(cached=cached)
            ]

    def nested_hydration(self) -> Dict[str, str]:
        """
        A dictionary that maps the entity id field name to the nested entity field name

        TODO: [SHU] replace this mapping by introducing `class WyvernField(pydantic.Field)`
        to represent the "entity ide field", which will reference to the nested entity field name
        """
        return {}


class WyvernEntity(WyvernDataModel):
    """
    WyvernEntity is a base class for all entities that have primary identifier.
    An entity is the basic unit of data that could be indexed and queried.
    """

    _identifier: Identifier = PrivateAttr()

    class Config:
        validate_assignment = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._identifier = self.generate_identifier()

    @property
    def identifier(self) -> Identifier:
        """
        This method returns the identifier for this entity
        """
        return self._identifier

    def generate_identifier(self) -> Identifier:
        raise NotImplementedError

    def dict(self, *args, **kwargs):
        results = super().dict(*args, **kwargs)
        # enrich data
        results.update({"identifier": self.identifier.dict()})
        return results

    def load_fields(self, data: Dict[str, Any]) -> None:
        """
        This method load the entity with the given data.
        The return data is the nested entities that need to be further hydrated

        For example:
            if a Product contains these two fields: `brand_id: Optional[str]` and `brand: Optional[Brand]`,
            as the hydrated entity. We fetch the brand_id for the product from Wyvern Index,
            as the first hydration step for Product entity, then we fetch brand entity from Wyvern Index,
            as the second hydration step
        """
        for field in self.__fields__:
            value = getattr(self, field)
            if value:
                continue
            if field in data:
                setattr(self, field, data[field])


class QueryEntity(WyvernEntity):
    """
    QueryEntity is a base class for all entities that have query as an identifier.

    Attributes:
        query: the query string
    """

    query: str

    def generate_identifier(self) -> Identifier:
        """
        This method returns the identifier for this entity.

        Returns:
            Identifier: the identifier for this entity with identifier_type=SimpleIdentifierType.QUERY.
        """
        return Identifier(
            identifier=self.query,
            identifier_type=SimpleIdentifierType.QUERY.value,
        )


class ProductEntity(WyvernEntity):
    """
    ProductEntity is a base class for all entities that have product_id as an identifier.

    Attributes:
        product_id: the product id
    """

    product_id: str

    def generate_identifier(self) -> Identifier:
        """
        This method returns the identifier for this entity.

        Returns:
            Identifier: the identifier for this entity with identifier_type=SimpleIdentifierType.PRODUCT.
        """
        return Identifier(
            identifier=self.product_id,
            identifier_type=SimpleIdentifierType.PRODUCT.value,
        )


class UserEntity(WyvernEntity):
    """
    UserEntity is a base class for all entities that have user_id as an identifier.

    Attributes:
        user_id: the user id
    """

    user_id: str

    def generate_identifier(self) -> Identifier:
        """
        This method returns the identifier for this entity.

        Returns:
            Identifier: the identifier for this entity with identifier_type=SimpleIdentifierType.USER.
        """
        return Identifier(
            identifier=self.user_id,
            identifier_type=SimpleIdentifierType.USER.value,
        )
