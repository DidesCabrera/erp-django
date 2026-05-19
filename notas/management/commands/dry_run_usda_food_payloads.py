from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable

from notas.application.dto.imported_food_dto import ImportedFoodDTO
from notas.application.services.food_imports.normalization import normalize_imported_food
from notas.application.services.food_imports.quality import evaluate_imported_food_quality
from notas.application.services.food_imports.usda.mapper import (
    USDA_SOURCE_DATASET_DEFAULT,
    map_usda_food_to_imported_food_dto,
)
from notas.application.services.food_imports.visibility_policy import (
    resolve_initial_food_visibility,
)
from notas.domain.models import Food, FoodSourceMetadata


@dataclass(frozen=True)
class DryRunPreparedFood:
    index: int
    dto: ImportedFoodDTO
    quality_score: int


@dataclass(frozen=True)
class DryRunIssueSample:
    index: int
    reason: str
    payload_type: str
    source_food_id: str = ""
    description: str = ""


@dataclass(frozen=True)
class DryRunUSDAFoodPayloadsResult:
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    would_import_rows: int
    failed_rows: int
    extended_rows: int
    hidden_rows: int
    reason_counts: dict[str, int] = field(default_factory=dict)
    issue_samples: dict[str, list[DryRunIssueSample]] = field(default_factory=dict)

    @property
    def skipped_rows(self) -> int:
        return self.invalid_rows + self.duplicate_rows + self.failed_rows


def dry_run_usda_food_payloads(
    *,
    payloads: Iterable[Any],
    source_version: str,
    source_dataset: str = USDA_SOURCE_DATASET_DEFAULT,
    sample_size: int = 0,
) -> DryRunUSDAFoodPayloadsResult:
    """
    Simulate a USDA import without writing anything to the database.

    Responsibilities:
    - map USDA payloads into ImportedFoodDTO
    - normalize DTOs
    - evaluate import quality
    - detect duplicates already imported in the database
    - detect duplicates inside the same file
    - estimate initial visibility for rows that would be imported
    - optionally collect small issue samples for operational reporting

    Data safety:
    - does not create Food records
    - does not create FoodSourceMetadata records
    - does not create FoodImportBatch records
    - does not mutate existing user or global foods
    """

    payload_list = list(payloads)
    reason_counts: Counter[str] = Counter()
    issue_samples: dict[str, list[DryRunIssueSample]] = defaultdict(list)
    prepared_foods: list[DryRunPreparedFood] = []

    invalid_rows = 0
    failed_rows = 0

    normalized_sample_size = max(sample_size, 0)

    for index, payload in enumerate(payload_list):
        try:
            dto = map_usda_food_to_imported_food_dto(
                payload,
                source_version=source_version,
                source_dataset=source_dataset,
            )
            normalized_dto = normalize_imported_food(dto)
            quality_result = evaluate_imported_food_quality(normalized_dto)

            if not quality_result.is_valid:
                invalid_rows += 1
                reason = quality_result.reason or "invalid"
                reason_counts[reason] += 1
                _append_issue_sample(
                    issue_samples=issue_samples,
                    sample_size=normalized_sample_size,
                    reason=reason,
                    index=index,
                    payload=payload,
                    source_food_id=normalized_dto.source_food_id,
                    description=normalized_dto.name,
                )
                continue

            prepared_foods.append(
                DryRunPreparedFood(
                    index=index,
                    dto=normalized_dto,
                    quality_score=quality_result.score,
                )
            )

        except Exception:
            failed_rows += 1
            reason_counts["mapping_failed"] += 1
            _append_issue_sample(
                issue_samples=issue_samples,
                sample_size=normalized_sample_size,
                reason="mapping_failed",
                index=index,
                payload=payload,
            )

    source_food_ids = [
        prepared_food.dto.source_food_id
        for prepared_food in prepared_foods
        if prepared_food.dto.source_food_id
    ]

    already_imported_source_ids = set(
        FoodSourceMetadata.objects.filter(
            source=FoodSourceMetadata.SOURCE_USDA,
            source_food_id__in=source_food_ids,
        ).values_list("source_food_id", flat=True)
    )

    seen_source_ids: set[str] = set()

    duplicate_rows = 0
    would_import_rows = 0
    extended_rows = 0
    hidden_rows = 0

    for prepared_food in prepared_foods:
        source_food_id = prepared_food.dto.source_food_id

        if source_food_id in seen_source_ids:
            duplicate_rows += 1
            reason_counts["duplicate_in_file"] += 1
            _append_issue_sample(
                issue_samples=issue_samples,
                sample_size=normalized_sample_size,
                reason="duplicate_in_file",
                index=prepared_food.index,
                payload=None,
                source_food_id=source_food_id,
                description=prepared_food.dto.name,
            )
            continue

        seen_source_ids.add(source_food_id)

        if source_food_id in already_imported_source_ids:
            duplicate_rows += 1
            reason_counts["already_imported"] += 1
            _append_issue_sample(
                issue_samples=issue_samples,
                sample_size=normalized_sample_size,
                reason="already_imported",
                index=prepared_food.index,
                payload=None,
                source_food_id=source_food_id,
                description=prepared_food.dto.name,
            )
            continue

        would_import_rows += 1

        visibility = resolve_initial_food_visibility(
            quality_score=prepared_food.quality_score,
        )

        if visibility == Food.VISIBILITY_EXTENDED:
            extended_rows += 1
        elif visibility == Food.VISIBILITY_HIDDEN:
            hidden_rows += 1

    return DryRunUSDAFoodPayloadsResult(
        total_rows=len(payload_list),
        valid_rows=len(prepared_foods),
        invalid_rows=invalid_rows,
        duplicate_rows=duplicate_rows,
        would_import_rows=would_import_rows,
        failed_rows=failed_rows,
        extended_rows=extended_rows,
        hidden_rows=hidden_rows,
        reason_counts=dict(reason_counts),
        issue_samples={
            reason: samples
            for reason, samples in issue_samples.items()
            if samples
        },
    )


def _append_issue_sample(
    *,
    issue_samples: dict[str, list[DryRunIssueSample]],
    sample_size: int,
    reason: str,
    index: int,
    payload: Any,
    source_food_id: str = "",
    description: str = "",
) -> None:
    if sample_size <= 0:
        return

    if len(issue_samples[reason]) >= sample_size:
        return

    extracted_source_food_id = source_food_id
    extracted_description = description

    if isinstance(payload, dict):
        extracted_source_food_id = extracted_source_food_id or str(payload.get("fdcId") or "")
        extracted_description = extracted_description or str(payload.get("description") or "")

    issue_samples[reason].append(
        DryRunIssueSample(
            index=index,
            reason=reason,
            payload_type=type(payload).__name__,
            source_food_id=extracted_source_food_id,
            description=extracted_description,
        )
    )