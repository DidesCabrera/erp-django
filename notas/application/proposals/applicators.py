from dataclasses import asdict, dataclass

from notas.application.proposals.operations import (
    OPERATION_UPDATE_MEAL_FOOD_QUANTITY,
)
from notas.application.proposals.validators import (
    ValidatedUpdateMealFoodQuantityOperation,
    validate_proposal_operations,
)
from notas.application.services.commands.meal_commands import (
    update_meal_food,
)
from notas.domain.models import (
    MealFood,
    NutritionProposal,
)


@dataclass(frozen=True)
class AppliedProposalOperation:
    type: str
    mealfood_id: int
    meal_id: int
    food_id: int
    food_name: str
    quantity_before: float
    quantity_after: float

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ProposalOperationsApplyResult:
    proposal: NutritionProposal
    applied_operations: list[AppliedProposalOperation]

    @property
    def applied_count(self) -> int:
        return len(self.applied_operations)

    def as_dict(self) -> dict:
        return {
            "proposal_id": self.proposal.id,
            "applied_count": self.applied_count,
            "applied_operations": [
                operation.as_dict()
                for operation in self.applied_operations
            ],
        }


def _get_mealfood_for_application(
    operation: ValidatedUpdateMealFoodQuantityOperation,
) -> MealFood:
    meal_food = (
        MealFood.objects
        .select_related(
            "meal",
            "food",
        )
        .get(pk=operation.mealfood_id)
    )

    return meal_food


def apply_update_meal_food_quantity_operation(
    operation: ValidatedUpdateMealFoodQuantityOperation,
) -> AppliedProposalOperation:
    meal_food = _get_mealfood_for_application(operation)

    quantity_before = float(meal_food.quantity)

    update_meal_food(
        meal_food=meal_food,
        quantity=operation.to_quantity,
    )

    meal_food.refresh_from_db()

    return AppliedProposalOperation(
        type=OPERATION_UPDATE_MEAL_FOOD_QUANTITY,
        mealfood_id=meal_food.id,
        meal_id=meal_food.meal_id,
        food_id=meal_food.food_id,
        food_name=meal_food.food.name,
        quantity_before=quantity_before,
        quantity_after=float(meal_food.quantity),
    )


def apply_validated_proposal_operations(
    *,
    proposal: NutritionProposal,
    operations: list[ValidatedUpdateMealFoodQuantityOperation],
) -> ProposalOperationsApplyResult:
    """
    Aplica operaciones ya validadas usando commands internos.

    Importante:
    esta función NO decide si la propuesta está aprobada o no.
    Esa regla vivirá en apply_approved_proposal en el siguiente bloque.
    """
    applied_operations = []

    for operation in operations:
        if operation.type == OPERATION_UPDATE_MEAL_FOOD_QUANTITY:
            applied_operations.append(
                apply_update_meal_food_quantity_operation(
                    operation,
                )
            )
            continue

        raise ValueError("unsupported_proposal_operation_type")

    return ProposalOperationsApplyResult(
        proposal=proposal,
        applied_operations=applied_operations,
    )


def validate_and_apply_proposal_operations(
    proposal: NutritionProposal,
) -> ProposalOperationsApplyResult:
    """
    Valida y aplica el payload de una propuesta.

    Importante:
    esta función todavía NO verifica status approved.
    Se usará como pieza interna del futuro command apply_approved_proposal.
    """
    operations = validate_proposal_operations(proposal)

    return apply_validated_proposal_operations(
        proposal=proposal,
        operations=operations,
    )