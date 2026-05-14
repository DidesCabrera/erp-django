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

    This command is intentionally small and controlled.

    Responsibilities:
    - receive USDA-like payloads
    - map each payload into ImportedFoodDTO
    - delegate persistence to import_food_batch

    Data safety rules:
    - this command does not directly create Food records
    - this command does not modify user foods
    - deduplication remains handled by source + source_food_id
    - quality validation remains handled by the generic import command
    """

    dtos = [
        map_usda_food_to_imported_food_dto(
            payload,
            source_version=source_version,
            source_dataset=source_dataset,
        )
        for payload in payloads
    ]

    batch_result = import_food_batch(
        source=FoodSourceMetadata.SOURCE_USDA,
        source_version=source_version,
        foods=dtos,
        notes=notes,
    )

    return ImportUSDAFoodPayloadsResult(
        batch_result=batch_result,
    )