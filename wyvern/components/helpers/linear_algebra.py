# -*- coding: utf-8 -*-
import asyncio
from typing import List, Tuple

from scipy.spatial.distance import cosine

from wyvern.components.component import Component


class CosineSimilarityComponent(
    Component[List[Tuple[List[float], List[float]]], List[float]],
):
    def __init__(self, name: str):
        super().__init__(name=name)

    async def execute(
        self,
        input: List[Tuple[List[float], List[float]]],
        **kwargs,
    ) -> List[float]:
        tasks = await asyncio.gather(
            *[
                self.cosine_similarity(embedding1, embedding2)
                for (embedding1, embedding2) in input
            ],
            return_exceptions=False,
        )
        # TODO (suchintan): Handle exceptions in cosine similarity function
        return list(tasks)

    async def cosine_similarity(
        self,
        embedding_1: List[float],
        embedding_2: List[float],
    ) -> float:
        return 1 - cosine(embedding_1, embedding_2)
