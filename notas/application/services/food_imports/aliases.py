from dataclasses import dataclass

from notas.application.services.food_imports.normalization import normalize_food_name
from notas.domain.models import Food, FoodAlias


@dataclass(frozen=True)
class FoodAliasInput:
    name: str
    language: str = "es"
    country: str = ""


@dataclass(frozen=True)
class EnsureFoodAliasesResult:
    created_count: int
    skipped_count: int


def ensure_food_aliases(
    *,
    food: Food,
    aliases: list[FoodAliasInput],
) -> EnsureFoodAliasesResult:
    """
    Ensure aliases exist for a food.

    This service is idempotent:
    - existing aliases are skipped
    - new aliases are created
    - normalized_name is generated consistently

    It does not modify the Food itself.
    """

    created_count = 0
    skipped_count = 0

    for alias_input in aliases:
        alias_name = _clean_alias_name(alias_input.name)

        if not alias_name:
            skipped_count += 1
            continue

        language = _clean_language(alias_input.language)
        country = _clean_country(alias_input.country)
        normalized_name = normalize_food_name(alias_name)

        _, created = FoodAlias.objects.get_or_create(
            food=food,
            normalized_name=normalized_name,
            language=language,
            country=country,
            defaults={
                "name": alias_name,
            },
        )

        if created:
            created_count += 1
        else:
            skipped_count += 1

    return EnsureFoodAliasesResult(
        created_count=created_count,
        skipped_count=skipped_count,
    )


def _clean_alias_name(value: str | None) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _clean_language(value: str | None) -> str:
    if not value:
        return "es"

    return str(value).strip().lower() or "es"


def _clean_country(value: str | None) -> str:
    if not value:
        return ""

    return str(value).strip().upper()