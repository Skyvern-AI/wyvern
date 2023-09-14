# -*- coding: utf-8 -*-
from functools import cached_property
from typing import Optional, Set

from wyvern.components.models.model_component import ModelComponent
from wyvern.entities.model_entities import MODEL_INPUT, MODEL_OUTPUT, ChainedModelInput
from wyvern.exceptions import MissingModelChainOutputError


class ModelChainComponent(ModelComponent[MODEL_INPUT, MODEL_OUTPUT]):
    """
    Model chaining allows you to chain models together so that the output of one model can be the input to another model

    For all the models in the chain, all the request and entities in the model input are the same
    """

    def __init__(self, *upstreams: ModelComponent, name: Optional[str] = None):
        super().__init__(*upstreams, name=name)
        self.chain = upstreams

    @cached_property
    def manifest_feature_names(self) -> Set[str]:
        feature_names: Set[str] = set()
        for model in self.chain:
            feature_names = feature_names.union(model.manifest_feature_names)
        return feature_names

    async def inference(self, input: MODEL_INPUT, **kwargs) -> MODEL_OUTPUT:
        output = None
        prev_model: Optional[ModelComponent] = None
        for model in self.chain:
            curr_input: ChainedModelInput
            if prev_model is not None and output is not None:
                curr_input = ChainedModelInput(
                    request=input.request,
                    entities=input.entities,
                    upstream_model_name=prev_model.name,
                    upstream_model_output=output.data,
                )
            else:
                curr_input = ChainedModelInput(
                    request=input.request,
                    entities=input.entities,
                    upstream_model_name=None,
                    upstream_model_output={},
                )
            output = await model.execute(curr_input, **kwargs)
            prev_model = model

        if output is None:
            raise MissingModelChainOutputError()

        # TODO: do type checking to make sure the output is of the correct type
        return output
