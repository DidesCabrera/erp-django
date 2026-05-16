from dataclasses import dataclass

from django.db import transaction

from notas.application.services.food_imports.aliases import ensure_food_aliases
from notas.application.services.food_imports.core_food_seed_catalog import (
    CoreFoodSeedItem,
    get_core_food_seed_by_canonical_name,
    get_core_food_seed_canonical_names,
)
from notas.application.services.food_imports.localized_names import (
    ensure_food_localized_names,
)
from notas.domain.models import Food


@dataclass(frozen=True)
class ApplyCoreFoodSeedResult:
    matched_foods: int
    promoted_foods: int
    created_aliases: int
    skipped_aliases: int
    created_localized_names: int
    updated_localized_names: int
    skipped_localized_names: int


def apply_core_food_seed_to_existing_global_foods() -> ApplyCoreFoodSeedResult:
    """
    Apply the initial core food seed catalog to existing global foods.

    This service:
    - matches foods by canonical_name
    - promotes matched global foods to core
    - marks them verified and active
    - creates Spanish aliases
    - creates localized display names

    It does not:
    - create missing Food records
    - modify nutrition values
    - modify user-created foods
    """

    seed_by_canonical_name = get_core_food_seed_by_canonical_name()

    foods = Food.objects.filter(
        is_global=True,
        canonical_name__in=get_core_food_seed_canonical_names(),
    )

    counters = _MutableCoreFoodSeedCounters()

    with transaction.atomic():
        for food in foods:
            seed_item = seed_by_canonical_name.get(food.canonical_name)

            if seed_item is None:
                continue

            counters.matched_foods += 1

            _promote_food_to_core(food)
            counters.promoted_foods += 1

            _apply_seed_item_to_food(
                food=food,
                seed_item=seed_item,
                counters=counters,
            )

    return counters.to_result()


def _promote_food_to_core(food: Food) -> None:
    food.visibility = Food.VISIBILITY_CORE
    food.is_verified = True
    food.is_active = True
    food.save(
        update_fields=[
            "visibility",
            "is_verified",
            "is_active",
        ]
    )


def _apply_seed_item_to_food(
    *,
    food: Food,
    seed_item: CoreFoodSeedItem,
    counters,
) -> None:
    alias_result = ensure_food_aliases(
        food=food,
        aliases=seed_item.aliases,
    )

    localized_name_result = ensure_food_localized_names(
        food=food,
        localized_names=seed_item.localized_names,
    )

    counters.created_aliases += alias_result.created_count
    counters.skipped_aliases += alias_result.skipped_count

    counters.created_localized_names += localized_name_result.created_count
    counters.updated_localized_names += localized_name_result.updated_count
    counters.skipped_localized_names += localized_name_result.skipped_count


@dataclass
class _MutableCoreFoodSeedCounters:
    matched_foods: int = 0
    promoted_foods: int = 0
    created_aliases: int = 0
    skipped_aliases: int = 0
    created_localized_names: int = 0
    updated_localized_names: int = 0
    skipped_localized_names: int = 0

    def to_result(self) -> ApplyCoreFoodSeedResult:
        return ApplyCoreFoodSeedResult(
            matched_foods=self.matched_foods,
            promoted_foods=self.promoted_foods,
            created_aliases=self.created_aliases,
            skipped_aliases=self.skipped_aliases,
            created_localized_names=self.created_localized_names,
            updated_localized_names=self.updated_localized_names,
            skipped_localized_names=self.skipped_localized_names,
        )