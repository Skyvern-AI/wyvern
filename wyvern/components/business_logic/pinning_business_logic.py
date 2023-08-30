# -*- coding: utf-8 -*-
import logging
from typing import Callable, Dict, Generic, List, Optional

from wyvern.components.business_logic.business_logic import BusinessLogicComponent
from wyvern.components.component import Component
from wyvern.entities.candidate_entities import (
    GENERALIZED_WYVERN_ENTITY,
    ScoredCandidate,
)
from wyvern.wyvern_typing import REQUEST_ENTITY

logger = logging.getLogger(__name__)


class PinningBusinessLogicComponent(
    BusinessLogicComponent[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
    Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
):
    """
    A component that performs boosting on an entity with a set of candidates

    The request itself could contain more than just entities, for example it may contain a query and so on
    """

    def __init__(self, *upstreams: Component):
        super().__init__(*upstreams, name=self.__class__.__name__)

    def pin(
        self,
        scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        entity_pins: Dict[str, int],
        entity_key_mapping: Callable[
            [GENERALIZED_WYVERN_ENTITY],
            str,
        ] = lambda candidate: candidate.identifier.identifier,
        allow_down_ranking: bool = False,
    ) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]:
        """
        Pins the supplied entity to the specific position

        Args:
            scored_candidates: The list of scored candidates
            entity_pins: The map of entity keys (unique identifiers) to pin, and their pinning position
            entity_key_mapping: A lambda function that takes in a candidate entity and
                returns the field we should apply the pin to
            allow_down_ranking: Whether to allow down-ranking of candidates that are not pinned

        Returns:
            The list of scored candidates with the pinned entities
        """
        applied_pins_score: Dict[int, float] = {}
        re_scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]] = []
        for index, candidate in enumerate(scored_candidates):
            current_position = len(scored_candidates) - index
            pin_candidate_new_position: Optional[int] = None
            # Determine which desired pins are applicable for this candidate set
            entity_key = entity_key_mapping(candidate.entity)
            if entity_key in entity_pins:
                desired_position = entity_pins[entity_key]

                if allow_down_ranking or desired_position < current_position:
                    pin_candidate_new_position = min(
                        desired_position,
                        len(scored_candidates) - 1,
                    )

            if pin_candidate_new_position is None:
                re_scored_candidates.append(candidate)
                continue

            pinned_score = self._get_pinned_score(
                applied_pins_score,
                candidate,
                pin_candidate_new_position,
                scored_candidates,
            )

            re_scored_candidates.append(
                ScoredCandidate(entity=candidate.entity, score=pinned_score),
            )

            self._update_applied_pins_score(
                applied_pins_score,
                pin_candidate_new_position,
                pinned_score,
            )

        return re_scored_candidates

    def _update_applied_pins_score(
        self,
        applied_pins_score: Dict[int, float],
        current_position: int,
        new_score: float,
    ):
        """
        Updates the applied pins score dictionary with the new score for the given position

        Args:
            applied_pins_score: The dictionary of applied pins score
            current_position: The current position to update
            new_score: The new score to apply
        """
        if current_position in applied_pins_score:
            # This means this position already had a pin applied to it.. so we need to update the position
            existing_pin_score = applied_pins_score[current_position]
            if existing_pin_score > new_score:
                # new_score is smaller, so let's update our memory of the pin to occupy the previous position
                self._update_applied_pins_score(
                    applied_pins_score,
                    current_position - 1,
                    existing_pin_score,
                )
            else:
                # new_score is higher, so let's update our memory of the pin to occupy the next position
                self._update_applied_pins_score(
                    applied_pins_score,
                    current_position + 1,
                    existing_pin_score,
                )

        applied_pins_score[current_position] = new_score

    def _get_pinned_score(
        self,
        applied_pins_score: Dict[int, float],
        candidate: ScoredCandidate[GENERALIZED_WYVERN_ENTITY],
        pin_candidate_new_position: int,
        scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
    ) -> float:
        """
        Gets the score for the pinned candidate

        Args:
            applied_pins_score: The dictionary of applied pins score
            candidate: The candidate to pin
            pin_candidate_new_position: The new position to pin the candidate to
            scored_candidates: The list of scored candidates

        Returns:
            The score for the pinned candidate
        """
        if pin_candidate_new_position >= len(scored_candidates) - 1:
            # Pinned position is outside or at the bottom of the candidate set,
            #   subtract current score from the lowest score
            # If there are multiple pins at the bottom, it will respect their relative score
            #   The reciprocal is used to ensure that higher scored products end up having a higher final score
            return scored_candidates[-1].score - (1.0 / candidate.score)
        elif pin_candidate_new_position == 0:
            # Pinned position is at the top of the candidate set -- add the highest score to the current candidate score
            # If there are multiple pins at position 1, it will currently respect their relative score
            # This makes sense to me, but we can change it if we want
            return scored_candidates[0].score + candidate.score
        else:
            # Average the scores of the candidates on either side of the pinned position
            left_position = pin_candidate_new_position
            right_position = pin_candidate_new_position + 1
            left_side_score = (
                scored_candidates[left_position].score
                if left_position not in applied_pins_score
                else applied_pins_score[left_position]
            )
            right_side_score = (
                scored_candidates[right_position].score
                if right_position not in applied_pins_score
                else applied_pins_score[right_position]
            )
            logger.debug(
                f"applied_pins_score={applied_pins_score} candidate={candidate.entity.get_all_identifiers()} "
                f"pin_candidate_new_position={pin_candidate_new_position} "
                f"left_side_score={left_side_score} right_side_score={right_side_score}",
            )
            return (left_side_score + right_side_score) / 2
