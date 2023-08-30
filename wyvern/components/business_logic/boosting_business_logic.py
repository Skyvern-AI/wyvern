# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Callable, Dict, Generic, List, Set

import pandas as pd
from pandas import DataFrame, Series

from wyvern.components.business_logic.business_logic import (
    BusinessLogicComponent,
    BusinessLogicRequest,
)
from wyvern.components.component import Component
from wyvern.entities.candidate_entities import (
    GENERALIZED_WYVERN_ENTITY,
    ScoredCandidate,
)
from wyvern.wyvern_typing import REQUEST_ENTITY

logger = logging.getLogger(__name__)


class BoostingBusinessLogicComponent(
    BusinessLogicComponent[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    """
    A component that performs boosting on an entity with a set of candidates. The boosting can be multiplicative
    or additive.

    The request itself could contain more than just entities, for example it may contain a query and so on
    """

    def __init__(self, *upstreams: Component):
        super().__init__(*upstreams, name=self.__class__.__name__)

    def boost(
        self,
        scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        entity_keys: Set[str],
        boost: float,
        entity_key_mapping: Callable[
            [GENERALIZED_WYVERN_ENTITY],
            str,
        ] = lambda candidate: candidate.identifier.identifier,
        multiplicative=False,
    ) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]:
        """
        Boosts the score of each candidate by a certain factor

        Args:
            scored_candidates: The list of scored candidates
            entity_keys: The set of entity keys (unique identifiers) to boost
            boost: The boost factor
            entity_key_mapping: A lambda function that takes in a candidate entity and
                returns the field we should apply the boost to
            multiplicative: Whether to apply the boost with multiplication or addition  - true indicates it is
                multiplication and false indicates it is addition

        Returns:
            The list of scored candidates with the boost applied
        """

        return [
            self._apply_boost_if_applicable(
                boost,
                candidate,
                entity_key_mapping,
                entity_keys,
                multiplicative,
            )
            for candidate in scored_candidates
        ]

    def _apply_boost_if_applicable(
        self,
        boost: float,
        candidate: ScoredCandidate[GENERALIZED_WYVERN_ENTITY],
        entity_key_mapping: Callable[[GENERALIZED_WYVERN_ENTITY], str],
        entity_keys: Set[str],
        multiplicative: bool,
    ) -> ScoredCandidate[GENERALIZED_WYVERN_ENTITY]:
        """
        Applies the boost to the candidate if the entity key is in the set of entity keys

        Args:
            boost: The boost factor
            candidate: The candidate to apply the boost to
            entity_key_mapping: A lambda function that takes in a candidate entity and
                returns the field we should apply the boost to
            entity_keys: The set of entity keys (unique identifiers) to boost
            multiplicative: Whether to apply the boost with multiplication or addition  - true indicates it is
                multiplication and false indicates it is addition

        Returns:
            The candidate with the boost applied
        """
        if entity_key_mapping(candidate.entity) in entity_keys:
            # TODO (suchintan): Should this be done in-place instead?
            new_score = (
                candidate.score * boost if multiplicative else candidate.score + boost
            )

            return ScoredCandidate(entity=candidate.entity, score=new_score)
        else:
            return candidate


# TODO (suchintan): Add a boost key class
# class BoostKey(BaseModel):


class CSVBoostingBusinessLogicComponent(
    BoostingBusinessLogicComponent[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    """
    This component reads a csv file and applies the boost based on specific column name, entity key, and score
    combinations

    Methods to define: Given a CSV row, generate the entity key and boost value

    Parameters:
        csv_file: The path to the CSV file
        multiplicative: Whether to apply the boost with multiplication or addition  - true indicates it is
                multiplication and false indicates it is addition
    """

    def __init__(self, *upstreams, csv_file: str, multiplicative: bool = False):
        self.csv_file = csv_file
        self.parsed_file: DataFrame = pd.DataFrame()
        self.lookup: Dict[str, float] = {}
        self.multiplicative = multiplicative
        super().__init__(*upstreams)

    async def initialize(self) -> None:
        """
        Reads the CSV file and populates the lookup table
        """
        self.parsed_file = pd.read_csv(self.csv_file)

        for _index, row in self.parsed_file.iterrows():
            key = await self.extract_keys_from_csv_row(row)
            boost = await self.extract_boost_value_from_csv_row(row)
            # TODO (suchintan): Handle collissions
            self.lookup[key] = boost

    @abstractmethod
    async def extract_keys_from_csv_row(self, row: Series) -> str:
        """
        Given a CSV row, generate the unique combinations that would apply a boost

        Example, in a file that has the following:
            product_id, query, boost

        The method would return a unique concatenation (ie product_id:query)
        """
        ...

    @abstractmethod
    async def extract_boost_value_from_csv_row(self, row: Series) -> float:
        """
        Given a CSV row, generate the unique combinations that would apply a boost

        Example, in a file that has the following:
            product_id, query, boost

        The method would return the boost value
        """
        ...

    @abstractmethod
    async def extract_key_from_request_entity(
        self,
        candidate: GENERALIZED_WYVERN_ENTITY,
        request: REQUEST_ENTITY,
    ) -> str:
        """
        Given a candidate and a request, generate a unique key that would apply a boost
        """
        ...

    async def execute(
        self,
        input: BusinessLogicRequest[
            GENERALIZED_WYVERN_ENTITY,
            REQUEST_ENTITY,
        ],
        **kwargs,
    ) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]:
        """
        Boosts the score of each candidate by a certain factor
        """
        re_scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]] = []
        for candidate in input.scored_candidates:
            key = await self.extract_key_from_request_entity(
                candidate.entity,
                input.request,
            )
            if key in self.lookup:
                new_score = (
                    candidate.score * self.lookup[key]
                    if self.multiplicative
                    else candidate.score + self.lookup[key]
                )
                re_scored_candidates.append(
                    ScoredCandidate(
                        entity=candidate.entity,
                        score=new_score,
                    ),
                )
            else:
                re_scored_candidates.append(candidate)

        return re_scored_candidates
