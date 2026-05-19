import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from notas.application.services.food_imports.usda.foundation_foods_reader import (
    FoundationFoodsReaderError,
    extract_foundation_food_payloads,
    read_foundation_food_payloads_from_json,
)


class FoundationFoodsReaderTests(SimpleTestCase):
    def test_extracts_payloads_from_direct_list(self):
        payloads = [
            {
                "fdcId": 1001,
                "description": "Oats, raw",
            }
        ]

        result = extract_foundation_food_payloads(payloads)

        self.assertEqual(result, payloads)

    def test_extracts_payloads_from_foundation_foods_root_key(self):
        payloads = [
            {
                "fdcId": 1002,
                "description": "Chicken breast, cooked",
            }
        ]

        result = extract_foundation_food_payloads(
            {
                "FoundationFoods": payloads,
                "metadata": {
                    "source": "USDA FoodData Central",
                },
            }
        )

        self.assertEqual(result, payloads)

    def test_extracts_payloads_from_lower_camel_root_key(self):
        payloads = [
            {
                "fdcId": 1003,
                "description": "Bananas, raw",
            }
        ]

        result = extract_foundation_food_payloads(
            {
                "foundationFoods": payloads,
            }
        )

        self.assertEqual(result, payloads)

    def test_rejects_object_without_supported_food_list(self):
        with self.assertRaises(FoundationFoodsReaderError):
            extract_foundation_food_payloads(
                {
                    "fdcId": 999,
                    "description": "Not a dataset root",
                }
            )

    def test_rejects_root_key_that_is_not_a_list(self):
        with self.assertRaises(FoundationFoodsReaderError):
            extract_foundation_food_payloads(
                {
                    "FoundationFoods": {
                        "fdcId": 1001,
                    }
                }
            )

    def test_allows_non_object_items_so_import_pipeline_can_count_mapping_failures(self):
        payloads = [
            {
                "fdcId": 1001,
            },
            "invalid item",
        ]

        result = extract_foundation_food_payloads(payloads)

        self.assertEqual(result, payloads)

    

    def test_reads_payloads_from_json_file(self):
        payloads = [
            {
                "fdcId": 1004,
                "description": "Rice, white, cooked",
            }
        ]

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

            result = read_foundation_food_payloads_from_json(path)

        self.assertEqual(result, payloads)

    def test_rejects_invalid_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "foundation_foods.json"
            path.write_text("{invalid json", encoding="utf-8")

            with self.assertRaises(FoundationFoodsReaderError):
                read_foundation_food_payloads_from_json(path)