from dataclasses import dataclass

from django.db import transaction

from notas.application.dto.imported_food_dto import ImportedFoodDTO
from notas.domain.models import Food, FoodSourceMetadata


@dataclass(frozen=True)
class ImportFoodFromSourceResult:
    food: Food
    created: bool
    skipped: bool
    reason: str = ""


def import_food_from_source(dto: ImportedFoodDTO) -> ImportFoodFromSourceResult:
    """
    Creates a global Food from an external source DTO.

    This command is intentionally source-agnostic. USDA, Open Food Facts,
    LATINFOODS or manual importers should map their data into ImportedFoodDTO
    before calling this command.

    Data safety rules:
    - Existing user foods are not modified.
    - Existing foods with the same source + source_food_id are not duplicated.
    - Imported foods are global, not user-owned.
    - Imported foods start unverified.
    """

    validation_error = _validate_imported_food(dto)
    if validation_error:
        return ImportFoodFromSourceResult(
            food=None,
            created=False,
            skipped=True,
            reason=validation_error,
        )

    existing_metadata = FoodSourceMetadata.objects.select_related("food").filter(
        source=dto.source,
        source_food_id=dto.source_food_id,
    ).first()

    if existing_metadata:
        return ImportFoodFromSourceResult(
            food=existing_metadata.food,
            created=False,
            skipped=True,
            reason="already_imported",
        )

    with transaction.atomic():
        food = Food.objects.create(
            name=dto.name,
            canonical_name=dto.canonical_name,
            protein=float(dto.protein),
            carbs=float(dto.carbs),
            fat=float(dto.fat),
            created_by=None,
            is_global=True,
            is_verified=False,
            is_active=True,
            food_group=dto.food_group,
            food_subgroup=dto.food_subgroup,
            fiber_g_per_100g=dto.fiber_g_per_100g,
            sugar_g_per_100g=dto.sugar_g_per_100g,
            saturated_fat_g_per_100g=dto.saturated_fat_g_per_100g,
            sodium_mg_per_100g=dto.sodium_mg_per_100g,
            visibility=Food.VISIBILITY_EXTENDED,
            data_quality_score=0,
        )

        FoodSourceMetadata.objects.create(
            food=food,
            source=dto.source,
            source_food_id=dto.source_food_id,
            source_dataset=dto.source_dataset,
            source_version=dto.source_version,
            source_url=dto.source_url,
            raw_payload_hash=dto.raw_payload_hash,
            normalized_payload_hash=dto.normalized_payload_hash,
            license_name=dto.license_name,
            attribution=dto.attribution,
        )

    return ImportFoodFromSourceResult(
        food=food,
        created=True,
        skipped=False,
    )


def _validate_imported_food(dto: ImportedFoodDTO) -> str:
    if not dto.source:
        return "missing_source"

    if not dto.source_food_id:
        return "missing_source_food_id"

    if not dto.name:
        return "missing_name"

    if dto.protein is None:
        return "missing_protein"

    if dto.carbs is None:
        return "missing_carbs"

    if dto.fat is None:
        return "missing_fat"

    if dto.protein < 0:
        return "invalid_negative_protein"

    if dto.carbs < 0:
        return "invalid_negative_carbs"

    if dto.fat < 0:
        return "invalid_negative_fat"

    return ""