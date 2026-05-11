from dataclasses import asdict, dataclass
from typing import Any

from notas.application.dto.proposal_payloads import (
    CREATE_MEAL_INTENT,
    ProposedMealPayloadDTO,
    parse_proposal_payload,
)
from notas.domain.models import NutritionProposal


@dataclass(frozen=True)
class ProposalApplyFoodDTO:
    food_id: int
    quantity: float
    unit: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ProposalApplyMealDTO:
    name: str
    foods: list[ProposalApplyFoodDTO]

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "foods": [
                food.as_dict()
                for food in self.foods
            ],
        }


@dataclass(frozen=True)
class ProposalApplyMealPlanDTO:
    proposal_id: int
    intent: str
    meal: ProposalApplyMealDTO

    def as_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "intent": self.intent,
            "meal": self.meal.as_dict(),
        }


def build_create_meal_apply_plan(
    *,
    proposal: NutritionProposal,
) -> ProposalApplyMealPlanDTO:
    """
    Construye un plan serializable para aplicar una proposal create_meal.

    Importante:
    - No crea Meal real.
    - No crea relaciones con Food.
    - No modifica DailyPlan.
    - Solo valida contrato y normaliza payload.
    """
    _ensure_proposal_is_approved_for_apply(
        proposal=proposal,
    )

    parsed_payload = parse_proposal_payload(
        _safe_dict(proposal.proposed_payload),
    )

    if not isinstance(parsed_payload, ProposedMealPayloadDTO):
        raise ValueError("proposal_apply_intent_must_be_create_meal")

    if parsed_payload.intent != CREATE_MEAL_INTENT:
        raise ValueError("proposal_apply_intent_must_be_create_meal")

    return ProposalApplyMealPlanDTO(
        proposal_id=proposal.id,
        intent=parsed_payload.intent,
        meal=ProposalApplyMealDTO(
            name=parsed_payload.meal.name,
            foods=[
                ProposalApplyFoodDTO(
                    food_id=food.food_id,
                    quantity=food.quantity,
                    unit=food.unit,
                )
                for food in parsed_payload.meal.foods
            ],
        ),
    )


def _ensure_proposal_is_approved_for_apply(
    *,
    proposal: NutritionProposal,
) -> None:
    if proposal.status != NutritionProposal.STATUS_APPROVED:
        raise ValueError("proposal_apply_requires_approved_status")


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}