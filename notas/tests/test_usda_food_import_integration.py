from django.test import TestCase

from notas.application.services.commands.import_food_from_source import import_food_from_source
from notas.application.services.food_imports.usda.mapper import (
    USDA_NUTRIENT_CARBS,
    USDA_NUTRIENT_FAT,
    USDA_NUTRIENT_FIBER,
    USDA_NUTRIENT_PROTEIN,
    map_usda_food_to_imported_food_dto,
)
from notas.domain.models import Food, FoodSourceMetadata


class USDAFoodImportIntegrationTests(TestCase):
    def test_usda_payload_can_be_mapped_and_imported_as_global_food(self):
        payload = {
            "fdcId": 12345,
            "description": "Oats, raw",
            "foodCategory": {
                "description": "Cereal Grains and Pasta",
            },
            "foodNutrients": [
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_PROTEIN,
                    },
                    "amount": 16.9,
                },
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_CARBS,
                    },
                    "amount": 66.3,
                },
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_FAT,
                    },
                    "amount": 6.9,
                },
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_FIBER,
                    },
                    "amount": 10.6,
                },
            ],
        }

        dto = map_usda_food_to_imported_food_dto(
            payload,
            source_version="2026-04",
            source_dataset="foundation_foods",
        )

        result = import_food_from_source(dto)

        self.assertTrue(result.created)
        self.assertFalse(result.skipped)

        food = result.food

        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(food.name, "Oats, raw")
        self.assertEqual(food.canonical_name, "oats raw")
        self.assertEqual(food.protein, 16.9)
        self.assertEqual(food.carbs, 66.3)
        self.assertEqual(food.fat, 6.9)
        self.assertEqual(food.food_group, "cereal_grains_and_pasta")
        self.assertTrue(food.is_global)
        self.assertEqual(food.category, "system")

        metadata = FoodSourceMetadata.objects.get(food=food)

        self.assertEqual(metadata.source, FoodSourceMetadata.SOURCE_USDA)
        self.assertEqual(metadata.source_food_id, "12345")
        self.assertEqual(metadata.source_dataset, "foundation_foods")
        self.assertEqual(metadata.source_version, "2026-04")
        self.assertEqual(metadata.license_name, "CC0")
        self.assertEqual(metadata.attribution, "USDA FoodData Central")