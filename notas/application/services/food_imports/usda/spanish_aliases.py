from dataclasses import dataclass

from notas.application.services.food_imports.aliases import ensure_food_aliases
from notas.application.services.food_imports.usda.spanish_alias_catalog import (
    USDA_SPANISH_ALIAS_CATALOG,
)
from notas.domain.models import Food


@dataclass(frozen=True)
class ApplyUSDASpanishAliasesResult:
    matched_foods: int
    created_aliases: int
    skipped_aliases: int


def apply_usda_spanish_aliases_to_foods(
    *,
    foods,
) -> ApplyUSDASpanishAliasesResult:
    """
    Apply known Spanish aliases to USDA/global foods.

    This service is intentionally conservative:
    - it only matches by canonical_name;
    - it only applies aliases present in the explicit catalog;
    - it does not rename foods;
    - it does not modify nutrition values.
    """

    matched_foods = 0
    created_aliases = 0
    skipped_aliases = 0

    for food in foods:
        aliases = USDA_SPANISH_ALIAS_CATALOG.get(food.canonical_name)

        if not aliases:
            continue

        matched_foods += 1

        result = ensure_food_aliases(
            food=food,
            aliases=aliases,
        )

        created_aliases += result.created_count
        skipped_aliases += result.skipped_count

    return ApplyUSDASpanishAliasesResult(
        matched_foods=matched_foods,
        created_aliases=created_aliases,
        skipped_aliases=skipped_aliases,
    )


def apply_usda_spanish_aliases_to_visible_global_foods() -> ApplyUSDASpanishAliasesResult:
    foods = Food.objects.filter(
        is_global=True,
        is_active=True,
        visibility__in=[
            Food.VISIBILITY_CORE,
            Food.VISIBILITY_EXTENDED,
        ],
    )

    return apply_usda_spanish_aliases_to_foods(
        foods=foods,
    )