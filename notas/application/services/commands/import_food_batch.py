from dataclasses import dataclass
from typing import Iterable

from django.utils import timezone

from notas.domain.models import FoodImportBatch
from notas.application.services.commands.import_food_from_source import import_food_from_source
from notas.application.dto.imported_food_dto import ImportedFoodDTO


@dataclass(frozen=True)
class ImportFoodBatchResult:
    batch: FoodImportBatch
    total_rows: int
    imported_rows: int
    skipped_rows: int
    failed_rows: int


def import_food_batch(
    *,
    source: str,
    source_version: str,
    foods: Iterable[ImportedFoodDTO],
    notes: str = "",
) -> ImportFoodBatchResult:
    """
    Imports a collection of ImportedFoodDTO records and tracks the process
    in FoodImportBatch.

    This command is source-agnostic. USDA, Open Food Facts or LATINFOODS
    importers should map their rows into ImportedFoodDTO before calling it.

    Data safety rules:
    - Existing imported foods are not duplicated.
    - Invalid rows are skipped by the individual import command.
    - Unexpected exceptions are counted as failed rows.
    - Existing user foods are not modified.
    """

    food_list = list(foods)

    batch = FoodImportBatch.objects.create(
        source=source,
        source_version=source_version,
        status=FoodImportBatch.STATUS_RUNNING,
        total_rows=len(food_list),
        imported_rows=0,
        skipped_rows=0,
        failed_rows=0,
        notes=notes,
    )

    imported_rows = 0
    skipped_rows = 0
    failed_rows = 0

    for dto in food_list:
        try:
            result = import_food_from_source(dto)

            if result.created:
                imported_rows += 1
            elif result.skipped:
                skipped_rows += 1
            else:
                failed_rows += 1

        except Exception:
            failed_rows += 1

    if failed_rows:
        status = FoodImportBatch.STATUS_COMPLETED_WITH_ERRORS
    else:
        status = FoodImportBatch.STATUS_COMPLETED

    batch.imported_rows = imported_rows
    batch.skipped_rows = skipped_rows
    batch.failed_rows = failed_rows
    batch.status = status
    batch.finished_at = timezone.now()
    batch.save(
        update_fields=[
            "imported_rows",
            "skipped_rows",
            "failed_rows",
            "status",
            "finished_at",
        ]
    )

    return ImportFoodBatchResult(
        batch=batch,
        total_rows=batch.total_rows,
        imported_rows=imported_rows,
        skipped_rows=skipped_rows,
        failed_rows=failed_rows,
    )