from decimal import Decimal

from django.test import SimpleTestCase

from notas.application.services.food_imports.usda.mapper import (
    USDA_NUTRIENT_CARBS,
    USDA_NUTRIENT_FAT,
    USDA_NUTRIENT_FIBER,
    USDA_NUTRIENT_PROTEIN,
    USDA_NUTRIENT_SATURATED_FAT,
    USDA_NUTRIENT_SODIUM,
    USDA_NUTRIENT_SUGARS,
    map_usda_food_to_imported_food_dto,
)
from notas.domain.models import FoodSourceMetadata


class USDAFoodMapperTests(SimpleTestCase):
    def test_map_usda_food_to_imported_food_dto_maps_required_fields(self):
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
                        "name": "Protein",
                        "unitName": "g",
                    },
                    "amount": 16.9,
                },
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_CARBS,
                        "name": "Carbohydrate, by difference",
                        "unitName": "g",
                    },
                    "amount": 66.3,
                },
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_FAT,
                        "name": "Total lipid (fat)",
                        "unitName": "g",
                    },
                    "amount": 6.9,
                },
            ],
        }

        dto = map_usda_food_to_imported_food_dto(
            payload,
            source_version="2026-04",
            source_dataset="foundation_foods",
        )

        self.assertEqual(dto.source, FoodSourceMetadata.SOURCE_USDA)
        self.assertEqual(dto.source_food_id, "12345")
        self.assertEqual(dto.source_dataset, "foundation_foods")
        self.assertEqual(dto.source_version, "2026-04")
        self.assertEqual(dto.name, "Oats, raw")
        self.assertEqual(dto.canonical_name, "Oats, raw")
        self.assertEqual(dto.protein, Decimal("16.9"))
        self.assertEqual(dto.carbs, Decimal("66.3"))
        self.assertEqual(dto.fat, Decimal("6.9"))
        self.assertEqual(dto.food_group, "Cereal Grains and Pasta")
        self.assertEqual(dto.license_name, "CC0")
        self.assertEqual(dto.attribution, "USDA FoodData Central")

    def test_map_usda_food_to_imported_food_dto_maps_optional_nutrients(self):
        payload = {
            "fdcId": 12345,
            "description": "Oats, raw",
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
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_SUGARS,
                    },
                    "amount": 0.9,
                },
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_SATURATED_FAT,
                    },
                    "amount": 1.2,
                },
                {
                    "nutrient": {
                        "number": USDA_NUTRIENT_SODIUM,
                    },
                    "amount": 2,
                },
            ],
        }

        dto = map_usda_food_to_imported_food_dto(
            payload,
            source_version="2026-04",
        )

        self.assertEqual(dto.fiber_g_per_100g, Decimal("10.6"))
        self.assertEqual(dto.sugar_g_per_100g, Decimal("0.9"))
        self.assertEqual(dto.saturated_fat_g_per_100g, Decimal("1.2"))
        self.assertEqual(dto.sodium_mg_per_100g, Decimal("2"))

    def test_map_usda_food_to_imported_food_dto_defaults_missing_required_nutrients_to_zero(self):
        payload = {
            "fdcId": 12345,
            "description": "Incomplete food",
            "foodNutrients": [],
        }

        dto = map_usda_food_to_imported_food_dto(
            payload,
            source_version="2026-04",
        )

        self.assertEqual(dto.protein, Decimal("0"))
        self.assertEqual(dto.carbs, Decimal("0"))
        self.assertEqual(dto.fat, Decimal("0"))

    def test_map_usda_food_to_imported_food_dto_handles_string_food_category(self):
        payload = {
            "fdcId": 12345,
            "description": "Banana, raw",
            "foodCategory": "Fruits and Fruit Juices",
            "foodNutrients": [],
        }

        dto = map_usda_food_to_imported_food_dto(
            payload,
            source_version="2026-04",
        )

        self.assertEqual(dto.food_group, "Fruits and Fruit Juices")