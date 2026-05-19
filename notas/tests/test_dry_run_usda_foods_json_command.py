import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from notas.application.services.food_imports.usda.mapper import (
    USDA_NUTRIENT_CARBS,
    USDA_NUTRIENT_FAT,
    USDA_NUTRIENT_PROTEIN,
)
from notas.domain.models import Food, FoodImportBatch, FoodSourceMetadata


def _usda_payload(
    *,
    fdc_id,
    description,
    protein=10,
    carbs=20,
    fat=5,
):
    return {
        "fdcId": fdc_id,
        "description": description,
        "foodCategory": {
            "description": "Test Foods",
        },
        "foodNutrients": [
            {
                "nutrient": {"number": USDA_NUTRIENT_PROTEIN},
                "amount": protein,
            },
            {
                "nutrient": {"number": USDA_NUTRIENT_CARBS},
                "amount": carbs,
            },
            {
                "nutrient": {"number": USDA_NUTRIENT_FAT},
                "amount": fat,
            },
        ],
    }


class DryRunUSDAFoodsJSONCommandTests(TestCase):
    def test_command_reports_dry_run_without_writing_database_records(self):
        existing_food = Food.objects.create(
            name="Existing oats",
            canonical_name="existing oats",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
        )

        FoodSourceMetadata.objects.create(
            food=existing_food,
            source=FoodSourceMetadata.SOURCE_USDA,
            source_food_id="3001",
            source_dataset="foundation_foods",
            source_version="2026-04",
        )

        payloads = [
            _usda_payload(
                fdc_id=3001,
                description="Oats, raw already imported",
            ),
            _usda_payload(
                fdc_id=3002,
                description="Rice, white, cooked",
            ),
            _usda_payload(
                fdc_id=3003,
                description="Chicken breast, cooked",
            ),
            _usda_payload(
                fdc_id=3003,
                description="Chicken breast, cooked duplicate in file",
            ),
            _usda_payload(
                fdc_id="",
                description="Invalid missing external id",
            ),
        ]

        out = StringIO()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "foundation_foods.json"
            path.write_text(
                json.dumps(
                    {
                        "FoundationFoods": payloads,
                    }
                ),
                encoding="utf-8",
            )

            call_command(
                "dry_run_usda_foods_json",
                str(path),
                source_version="2026-04",
                source_dataset="foundation_foods",
                stdout=out,
            )

        output = out.getvalue()

        self.assertIn("USDA dry-run completed.", output)
        self.assertIn("total=5", output)
        self.assertIn("valid=4", output)
        self.assertIn("invalid=1", output)
        self.assertIn("duplicates=2", output)
        self.assertIn("failed=0", output)
        self.assertIn("would_import=2", output)
        self.assertIn("would_skip=3", output)
        self.assertIn("visibility_extended=2", output)
        self.assertIn("- already_imported: 1", output)
        self.assertIn("- duplicate_in_file: 1", output)
        self.assertIn("- missing_source_food_id: 1", output)

        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodSourceMetadata.objects.count(), 1)
        self.assertEqual(FoodImportBatch.objects.count(), 0)

    def test_command_rejects_missing_file(self):
        with self.assertRaises(CommandError):
            call_command(
                "dry_run_usda_foods_json",
                "missing-file.json",
                source_version="2026-04",
            )

    def test_command_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.json"
            path.write_text("{invalid json", encoding="utf-8")

            with self.assertRaises(CommandError):
                call_command(
                    "dry_run_usda_foods_json",
                    str(path),
                    source_version="2026-04",
                )


    def test_command_can_show_issue_samples(self):
        payloads = [
            _usda_payload(
                fdc_id=3101,
                description="Rice, white, cooked",
            ),
            "invalid non object row",
        ]

        out = StringIO()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "foundation_foods.json"
            path.write_text(
                json.dumps(
                    {
                        "FoundationFoods": payloads,
                    }
                ),
                encoding="utf-8",
            )

            call_command(
                "dry_run_usda_foods_json",
                str(path),
                source_version="2026-04",
                source_dataset="foundation_foods",
                show_samples=True,
                sample_size=3,
                stdout=out,
            )

        output = out.getvalue()

        self.assertIn("USDA dry-run completed.", output)
        self.assertIn("total=2", output)
        self.assertIn("valid=1", output)
        self.assertIn("failed=1", output)
        self.assertIn("- mapping_failed: 1", output)
        self.assertIn("samples:", output)
        self.assertIn("- mapping_failed:", output)
        self.assertIn("index=1", output)
        self.assertIn("payload_type=str", output)
        self.assertIn("source_food_id=(none)", output)
        self.assertIn("description=(none)", output)