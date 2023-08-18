# -*- coding: utf-8 -*-
import asyncio
from functools import cached_property
from typing import Dict, Generic, List, Optional, Set, Union

from wyvern.components.models.model_component import (
    GENERALIZED_WYVERN_ENTITY,
    MODEL_OUTPUT_DATA_TYPE,
    REQUEST_ENTITY,
    ModelComponent,
    ModelInput,
    ModelOutput,
    SingleEntityInput,
)
from wyvern.entities.identifier import Identifier


class BaseRankingModel(
    ModelComponent[
        ModelInput[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        ModelOutput[MODEL_OUTPUT_DATA_TYPE],
    ],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY, MODEL_OUTPUT_DATA_TYPE],
):
    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        return set()

    async def single_inference(
        self,
        input: SingleEntityInput[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
    ) -> Union[float, str, List[float]]:
        """
        Single inference for ranking model
        """
        raise NotImplementedError

    async def inference(
        self,
        input: ModelInput[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        **kwargs,
    ) -> ModelOutput[MODEL_OUTPUT_DATA_TYPE]:
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
        output_data: Dict[Identifier, Optional[MODEL_OUTPUT_DATA_TYPE]] = {
            entity.identifier: model_score_batches[i]
            for i, entity in enumerate(input.entities)
        }
        return ModelOutput[MODEL_OUTPUT_DATA_TYPE](
            data=output_data,
            model_name=self.name,
        )
