import json
import tempfile
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


class ImportUSDAFoodsJSONCommandTests(TestCase):
    def test_command_imports_usda_foods_from_json_file(self):
        payloads = [
            {
                "fdcId": 2001,
                "description": "Rice, white, cooked",
                "foodCategory": {
                    "description": "Cereal Grains and Pasta",
                },
                "foodNutrients": [
                    {
                        "nutrient": {"number": USDA_NUTRIENT_PROTEIN},
                        "amount": 2.69,
                    },
                    {
                        "nutrient": {"number": USDA_NUTRIENT_CARBS},
                        "amount": 28.2,
                    },
                    {
                        "nutrient": {"number": USDA_NUTRIENT_FAT},
                        "amount": 0.28,
                    },
                ],
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample_usda.json"
            path.write_text(
                json.dumps(payloads),
                encoding="utf-8",
            )

            call_command(
                "import_usda_foods_json",
                str(path),
                source_version="2026-04",
                source_dataset="foundation_foods",
                notes="Test import command",
            )

        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodSourceMetadata.objects.count(), 1)
        self.assertEqual(FoodImportBatch.objects.count(), 1)

        food = Food.objects.get(canonical_name="rice white cooked")
        metadata = FoodSourceMetadata.objects.get(food=food)
        batch = FoodImportBatch.objects.get()

        self.assertTrue(food.is_global)
        self.assertEqual(food.category, "system")
        self.assertEqual(metadata.source, FoodSourceMetadata.SOURCE_USDA)
        self.assertEqual(metadata.source_food_id, "2001")
        self.assertEqual(metadata.source_version, "2026-04")
        self.assertEqual(batch.imported_rows, 1)
        self.assertEqual(batch.skipped_rows, 0)
        self.assertEqual(batch.failed_rows, 0)

    def test_command_rejects_missing_file(self):
        with self.assertRaises(CommandError):
            call_command(
                "import_usda_foods_json",
                "missing-file.json",
                source_version="2026-04",
            )

    def test_command_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.json"
            path.write_text("{invalid json", encoding="utf-8")

            with self.assertRaises(CommandError):
                call_command(
                    "import_usda_foods_json",
                    str(path),
                    source_version="2026-04",
                )

    def test_command_rejects_json_root_that_is_not_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid_root.json"
            path.write_text(
                json.dumps({"fdcId": 1}),
                encoding="utf-8",
            )

            with self.assertRaises(CommandError):
                call_command(
                    "import_usda_foods_json",
                    str(path),
                    source_version="2026-04",
                )