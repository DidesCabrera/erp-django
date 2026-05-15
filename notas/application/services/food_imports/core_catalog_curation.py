from dataclasses import dataclass

from notas.application.services.food_imports.core_catalog import (
    INITIAL_CORE_FOOD_CANONICAL_NAMES,
)
from notas.domain.models import Food


@dataclass(frozen=True)
class PromoteInitialCoreFoodsResult:
    matched_foods: int
    promoted_foods: int


def promote_initial_core_foods() -> PromoteInitialCoreFoodsResult:
    """
    Promote known useful global foods to the initial core catalog.

    This service is intentionally explicit and conservative.

    It only promotes foods whose canonical_name is present in the
    INITIAL_CORE_FOOD_CANONICAL_NAMES catalog.

    It does not change nutrition values.
    It does not modify user foods.
    """

    foods = Food.objects.filter(
        is_global=True,
        canonical_name__in=INITIAL_CORE_FOOD_CANONICAL_NAMES,
    )

    matched_foods = foods.count()

    promoted_foods = foods.update(
        visibility=Food.VISIBILITY_CORE,
        is_verified=True,
        is_active=True,
    )

    return PromoteInitialCoreFoodsResult(
        matched_foods=matched_foods,
        promoted_foods=promoted_foods,
    )