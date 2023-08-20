# -*- coding: utf-8 -*-
import asyncio
from typing import List, Union

from wyvern.components.models.model_component import (
    MODEL_INPUT,
    MODEL_OUTPUT,
    ModelComponent,
    SingleEntityInput,
)


class BaseRankingModel(ModelComponent[MODEL_INPUT, MODEL_OUTPUT]):
    async def single_inference(
        self,
        input: SingleEntityInput,
    ) -> Union[float, str, List[float]]:
        """
        Single inference for ranking model
        """
        raise NotImplementedError

    async def batch_inference(
        self,
        input: MODEL_INPUT,
    ) -> MODEL_OUTPUT:
        """
        Batch inference for ranking model
        """
        model_score_batches = await asyncio.gather(
            *[
                self.single_inference(
                    SingleEntityInput(entity=entity, request=input.request),
                )
                for entity in input.entities
            ]
        )
        output_data = {
            entity.identifier: model_score_batches[i]
            for i, entity in enumerate(input.entities)
        }
        return self.model_output_type(
            data=output_data,
            model_name=self.name,
        )

    async def inference(
        self,
        input: MODEL_INPUT,
        **kwargs,
    ) -> MODEL_OUTPUT:
        return await self.batch_inference(input)
