# -*- coding: utf-8 -*-
from typing import Optional

from wyvern.components.models.model_component import BaseModelComponent
from wyvern.entities.model_entities import MODEL_OUTPUT
from wyvern.wyvern_typing import INPUT_TYPE


class ModelExperimentation(BaseModelComponent[INPUT_TYPE, MODEL_OUTPUT]):
    def __init__(
        self,
        *upstreams,
        first_model: BaseModelComponent[INPUT_TYPE, MODEL_OUTPUT],
        second_model: BaseModelComponent[INPUT_TYPE, MODEL_OUTPUT],
        name: Optional[str] = None,
    ):
        super().__init__(*upstreams, name=name)
        self.first_model = first_model
        self.second_model = second_model

    async def execute(self, input: INPUT_TYPE, **kwargs) -> MODEL_OUTPUT:
        return await super().execute(input, **kwargs)
