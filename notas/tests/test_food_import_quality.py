from decimal import Decimal

from django.test import SimpleTestCase

from notas.application.dto.imported_food_dto import ImportedFoodDTO
from notas.application.services.food_imports.quality import evaluate_imported_food_quality


class FoodImportQualityTests(SimpleTestCase):
    def test_quality_accepts_valid_food(self):
        dto = ImportedFoodDTO(
            source="usda",
            source_food_id="12345",
            source_dataset="foundation_foods",
            source_version="2026-04",
            name="Oats",
            canonical_name="oats",
            protein=Decimal("16.9"),
            carbs=Decimal("66.3"),
            fat=Decimal("6.9"),
            food_group="cereals",
            food_subgroup="oats",
            fiber_g_per_100g=Decimal("10.6"),
            sugar_g_per_100g=Decimal("0.9"),
            saturated_fat_g_per_100g=Decimal("1.2"),
            sodium_mg_per_100g=Decimal("2"),
        )

        result = evaluate_imported_food_quality(dto)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.reason, "valid")
        self.assertGreater(result.score, 60)

    def test_quality_rejects_missing_name(self):
        dto = ImportedFoodDTO(
            source="usda",
            source_food_id="12345",
            source_dataset="foundation_foods",
            source_version="2026-04",
            name="",
            canonical_name="oats",
            protein=Decimal("16.9"),
            carbs=Decimal("66.3"),
            fat=Decimal("6.9"),
        )

        result = evaluate_imported_food_quality(dto)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "missing_name")

    def test_quality_rejects_negative_macro(self):
        dto = ImportedFoodDTO(
            source="usda",
            source_food_id="12345",
            source_dataset="foundation_foods",
            source_version="2026-04",
            name="Invalid Food",
            canonical_name="invalid food",
            protein=Decimal("-1"),
            carbs=Decimal("66.3"),
            fat=Decimal("6.9"),
        )

        result = evaluate_imported_food_quality(dto)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "invalid_negative_protein")

    def test_quality_rejects_macro_over_100g(self):
        dto = ImportedFoodDTO(
            source="usda",
            source_food_id="12345",
            source_dataset="foundation_foods",
            source_version="2026-04",
            name="Invalid Food",
            canonical_name="invalid food",
            protein=Decimal("101"),
            carbs=Decimal("0"),
            fat=Decimal("0"),
        )

        result = evaluate_imported_food_quality(dto)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "invalid_protein_over_100g")

    def test_quality_rejects_total_macros_over_limit(self):
        dto = ImportedFoodDTO(
            source="usda",
            source_food_id="12345",
            source_dataset="foundation_foods",
            source_version="2026-04",
            name="Invalid Food",
            canonical_name="invalid food",
            protein=Decimal("60"),
            carbs=Decimal("60"),
            fat=Decimal("10"),
        )

        result = evaluate_imported_food_quality(dto)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "invalid_total_macros_over_limit")

    def test_quality_rejects_invalid_sodium(self):
        dto = ImportedFoodDTO(
            source="usda",
            source_food_id="12345",
            source_dataset="foundation_foods",
            source_version="2026-04",
            name="Invalid Sodium Food",
            canonical_name="invalid sodium food",
            protein=Decimal("10"),
            carbs=Decimal("10"),
            fat=Decimal("10"),
            sodium_mg_per_100g=Decimal("100001"),
        )

        result = evaluate_imported_food_quality(dto)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.reason, "invalid_sodium_mg_per_100g_over_limit")