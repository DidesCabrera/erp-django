from dataclasses import asdict, dataclass

from notas.application.proposals.operations import (
    OPERATION_UPDATE_MEAL_FOOD_QUANTITY,
    UpdateMealFoodQuantityOperation,
    parse_proposal_operations,
)
from notas.domain.models import (
    DailyPlanMeal,
    MealFood,
    NutritionProposal,
)


@dataclass(frozen=True)
class ValidatedUpdateMealFoodQuantityOperation:
    type: str
    mealfood_id: int
    meal_id: int
    food_id: int
    food_name: str
    from_quantity: float
    to_quantity: float

    def as_dict(self) -> dict:
        return asdict(self)


def _quantities_match(
    left: float,
    right: float,
) -> bool:
    return abs(float(left) - float(right)) < 0.0001


def _get_mealfood_for_update_operation(
    operation: UpdateMealFoodQuantityOperation,
) -> MealFood:
    mealfood = (
        MealFood.objects
        .select_related(
            "meal",
            "food",
        )
        .filter(pk=operation.mealfood_id)
        .first()
    )

    if not mealfood:
        raise ValueError("proposal_operation_mealfood_not_found")

    return mealfood


def _ensure_mealfood_belongs_to_dailyplan(
    *,
    mealfood: MealFood,
    proposal: NutritionProposal,
) -> None:
    exists_in_dailyplan = DailyPlanMeal.objects.filter(
        dailyplan=proposal.dailyplan,
        meal=mealfood.meal,
    ).exists()

    if not exists_in_dailyplan:
        raise ValueError("proposal_operation_mealfood_not_in_dailyplan")


def _validate_update_meal_food_quantity_operation(
    *,
    proposal: NutritionProposal,
    operation: UpdateMealFoodQuantityOperation,
) -> ValidatedUpdateMealFoodQuantityOperation:
    mealfood = _get_mealfood_for_update_operation(operation)

    _ensure_mealfood_belongs_to_dailyplan(
        mealfood=mealfood,
        proposal=proposal,
    )

    current_quantity = float(mealfood.quantity)

    if not _quantities_match(
        current_quantity,
        operation.from_quantity,
    ):
        raise ValueError("proposal_operation_from_quantity_mismatch")

    if _quantities_match(
        current_quantity,
        operation.to_quantity,
    ):
        raise ValueError("proposal_operation_to_quantity_unchanged")

    return ValidatedUpdateMealFoodQuantityOperation(
        type=OPERATION_UPDATE_MEAL_FOOD_QUANTITY,
        mealfood_id=mealfood.id,
        meal_id=mealfood.meal_id,
        food_id=mealfood.food_id,
        food_name=mealfood.food.name,
        from_quantity=operation.from_quantity,
        to_quantity=operation.to_quantity,
    )


def validate_proposal_operations(
    proposal: NutritionProposal,
) -> list[ValidatedUpdateMealFoodQuantityOperation]:
    operations = parse_proposal_operations(
        proposal.proposed_payload or {},
    )

    validated_operations = []

    for operation in operations:
        if operation.type == OPERATION_UPDATE_MEAL_FOOD_QUANTITY:
            validated_operations.append(
                _validate_update_meal_food_quantity_operation(
                    proposal=proposal,
                    operation=operation,
                )
            )
            continue

        raise ValueError("unsupported_proposal_operation_type")

    return validated_operations