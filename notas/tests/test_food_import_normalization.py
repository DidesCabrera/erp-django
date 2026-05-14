from decimal import Decimal

from django.test import SimpleTestCase

from notas.application.dto.imported_food_dto import ImportedFoodDTO
from notas.application.services.food_imports.normalization import (
    normalize_food_name,
    normalize_imported_food,
)


class FoodImportNormalizationTests(SimpleTestCase):
    def test_normalize_food_name_lowercases_strips_accents_and_collapses_spaces(self):
        result = normalize_food_name("  Avena   Integral Ácida  ")

        self.assertEqual(result, "avena integral acida")

    def test_normalize_imported_food_cleans_text_fields(self):
        dto = ImportedFoodDTO(
            source=" USDA ",
            source_food_id=" 12345 ",
            source_dataset=" Foundation Foods ",
            source_version=" 2026-04 ",
            name="  Oats   Raw  ",
            canonical_name="  OATS   RAW ",
            protein=Decimal("16.9"),
            carbs=Decimal("66.3"),
            fat=Decimal("6.9"),
            food_group=" Cereals ",
            food_subgroup=" Oats ",
            license_name=" CC0 ",
            attribution=" USDA FoodData Central ",
        )

        result = normalize_imported_food(dto)

        self.assertEqual(result.source, "usda")
        self.assertEqual(result.source_food_id, "12345")
        self.assertEqual(result.source_dataset, "foundation_foods")
        self.assertEqual(result.source_version, "2026-04")
        self.assertEqual(result.name, "Oats Raw")
        self.assertEqual(result.canonical_name, "oats raw")
        self.assertEqual(result.food_group, "cereals")
        self.assertEqual(result.food_subgroup, "oats")
        self.assertEqual(result.license_name, "CC0")
        self.assertEqual(result.attribution, "USDA FoodData Central")

    def test_normalize_imported_food_uses_name_as_canonical_name_when_missing(self):
        dto = ImportedFoodDTO(
            source="usda",
            source_food_id="12345",
            source_dataset="foundation_foods",
            source_version="2026-04",
            name="  Chicken   Breast  ",
            canonical_name="",
            protein=Decimal("31"),
            carbs=Decimal("0"),
            fat=Decimal("3.6"),
        )

        result = normalize_imported_food(dto)

        self.assertEqual(result.name, "Chicken Breast")
        self.assertEqual(result.canonical_name, "chicken breast")