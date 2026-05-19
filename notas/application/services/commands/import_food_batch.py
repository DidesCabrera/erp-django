from dataclasses import dataclass
from typing import Iterable

from django.utils import timezone

from notas.application.dto.imported_food_dto import ImportedFoodDTO
from notas.application.services.commands.import_food_from_source import (
    import_food_from_source,
)
from notas.domain.models import FoodImportBatch


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
    total_rows_override: int | None = None,
    initial_failed_rows: int = 0,
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

    Optional counters:
    - total_rows_override lets source-specific importers preserve the original
      source row count when some rows failed before DTO creation.
    - initial_failed_rows lets source-specific importers include mapping-level
      failures in the same FoodImportBatch.
    """

    food_list = list(foods)
    total_rows = total_rows_override if total_rows_override is not None else len(food_list)

    batch = FoodImportBatch.objects.create(
        source=source,
        source_version=source_version,
        status=FoodImportBatch.STATUS_RUNNING,
        total_rows=total_rows,
        imported_rows=0,
        skipped_rows=0,
        failed_rows=initial_failed_rows,
        notes=notes,
    )

    imported_rows = 0
    skipped_rows = 0
    failed_rows = initial_failed_rows

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