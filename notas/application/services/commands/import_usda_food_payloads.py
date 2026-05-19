from dataclasses import dataclass
from typing import Iterable

from notas.application.services.commands.import_food_batch import (
    ImportFoodBatchResult,
    import_food_batch,
)
from notas.application.services.food_imports.usda.mapper import (
    USDA_SOURCE_DATASET_DEFAULT,
    map_usda_food_to_imported_food_dto,
)
from notas.domain.models import FoodSourceMetadata


@dataclass(frozen=True)
class ImportUSDAFoodPayloadsResult:
    batch_result: ImportFoodBatchResult
    mapping_failed_rows: int = 0

    @property
    def batch(self):
        return self.batch_result.batch

    @property
    def total_rows(self):
        return self.batch_result.total_rows

    @property
    def imported_rows(self):
        return self.batch_result.imported_rows

    @property
    def skipped_rows(self):
        return self.batch_result.skipped_rows

    @property
    def failed_rows(self):
        return self.batch_result.failed_rows


def import_usda_food_payloads(
    *,
    payloads: Iterable[dict],
    source_version: str,
    source_dataset: str = USDA_SOURCE_DATASET_DEFAULT,
    notes: str = "",
) -> ImportUSDAFoodPayloadsResult:
    """
    Import USDA FoodData Central-like payloads through the existing food import pipeline.

    Responsibilities:
    - receive USDA-like payloads
    - map each payload into ImportedFoodDTO
    - count mapping-level failures without aborting the whole import
    - delegate persistence to import_food_batch

    Data safety rules:
    - this command does not directly create Food records
    - this command does not modify user foods
    - deduplication remains handled by source + source_food_id
    - quality validation remains handled by the generic import command
    - broken external rows are counted as failed rows in FoodImportBatch
    """

    payload_list = list(payloads)
    dtos = []
    mapping_failed_rows = 0

    for payload in payload_list:
        try:
            dto = map_usda_food_to_imported_food_dto(
                payload,
                source_version=source_version,
                source_dataset=source_dataset,
            )
            dtos.append(dto)
        except Exception:
            mapping_failed_rows += 1

    batch_result = import_food_batch(
        source=FoodSourceMetadata.SOURCE_USDA,
        source_version=source_version,
        foods=dtos,
        notes=notes,
        total_rows_override=len(payload_list),
        initial_failed_rows=mapping_failed_rows,
    )

    return ImportUSDAFoodPayloadsResult(
        batch_result=batch_result,
        mapping_failed_rows=mapping_failed_rows,
    )