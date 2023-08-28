# -*- coding: utf-8 -*-
from typing import List

from wyvern.components.component import Component
from wyvern.entities.candidate_entities import (
    GENERALIZED_WYVERN_ENTITY,
    ScoredCandidate,
)


class SortingComponent(
    Component[
        List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
    ],
):
    """
    Sorts a list of candidates based on a score.
    """

    async def execute(
        self,
        input: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        descending=True,
        **kwargs
    ) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]:
        """
        Sorts a list of candidates based on a score.

        Args:
            input: A list of candidates to be sorted. Each candidate must have a score.
            descending: Whether to sort in descending order. Defaults to True.

        Returns:
            A sorted list of candidates.
        """
        return sorted(input, key=lambda candidate: candidate.score, reverse=descending)
