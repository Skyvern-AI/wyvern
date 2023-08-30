# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic.generics import GenericModel

from wyvern.entities.identifier_entities import WyvernDataModel
from wyvern.wyvern_typing import GENERALIZED_WYVERN_ENTITY


# TODO (suchintan): This should be renamed to ScoredEntity probably
class ScoredCandidate(GenericModel, Generic[GENERALIZED_WYVERN_ENTITY]):
    """
    A candidate entity with a score.

    Attributes:
        entity: The candidate entity.
        score: The score of the candidate entity. Defaults to 0.0.
    """

    entity: GENERALIZED_WYVERN_ENTITY
    score: float = 0.0


class CandidateSetEntity(
    WyvernDataModel,
    GenericModel,
    Generic[GENERALIZED_WYVERN_ENTITY],
):
    """
    A set of candidate entities. This is a generic model that can be used to represent a set of candidate entities.

    Attributes:
        candidates: The list of candidate entities.
    """

    candidates: List[GENERALIZED_WYVERN_ENTITY]


CANDIDATE_SET_ENTITY = TypeVar("CANDIDATE_SET_ENTITY", bound=CandidateSetEntity)
