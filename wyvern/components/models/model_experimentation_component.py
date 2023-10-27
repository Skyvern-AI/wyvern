# -*- coding: utf-8 -*-
from typing import Dict, Optional

from wyvern.components.models.model_component import BaseModelComponent
from wyvern.entities.model_entities import MODEL_OUTPUT
from wyvern.experimentation.client import experimentation_client
from wyvern.wyvern_typing import INPUT_TYPE


class ModelExperimentation(BaseModelComponent[INPUT_TYPE, MODEL_OUTPUT]):
    def __init__(
        self,
        # TODO: find a better name for assignment_mapping
        # this is the assignment var -> model mapping
        assignment_mapping: Dict[str, BaseModelComponent[INPUT_TYPE, MODEL_OUTPUT]],
        experiment_id: str,
        raise_error_on_none: bool = True,
        name: Optional[str] = None,
    ):
        all_models = list(assignment_mapping.values())
        super().__init__(*all_models, name=name)
        self.experiment_id = experiment_id
        self.assignment_mapping = assignment_mapping
        self.raise_error_on_none = raise_error_on_none

    async def execute(self, input: INPUT_TYPE, **kwargs) -> MODEL_OUTPUT:
        treatment = experimentation_client.get_experiment_result(
            self.experiment_id,
            self.get_entity_id(input),
        )
        # TODO: validation
        if treatment is None:
            # if self.raise_error_on_none:
            #     raise ValueError("treatment is None")
            # else:
            #     # use a default model?
            raise ValueError("treatment is None")

        model = self.assignment_mapping[treatment]
        return await model.execute(input, **kwargs)

    def get_entity_id(self, input: INPUT_TYPE) -> str:
        raise NotImplementedError
