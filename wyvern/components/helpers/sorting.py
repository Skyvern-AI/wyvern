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
    def __init__(self, name: str):
        super().__init__(name=name)

    async def execute(
        self,
        input: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        descending=True,
        **kwargs
    ) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]:
        return sorted(input, key=lambda candidate: candidate.score, reverse=descending)
