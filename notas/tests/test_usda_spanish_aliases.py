from django.test import TestCase

from notas.application.services.food_imports.usda.spanish_aliases import (
    apply_usda_spanish_aliases_to_foods,
    apply_usda_spanish_aliases_to_visible_global_foods,
)
from notas.domain.models import Food, FoodAlias


class USDASpanishAliasesTests(TestCase):
    def setUp(self):
        self.oats = Food.objects.create(
            name="Oats, raw",
            canonical_name="oats raw",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
        )

        self.chicken = Food.objects.create(
            name="Chicken breast, cooked",
            canonical_name="chicken breast cooked",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
        )

        self.unknown = Food.objects.create(
            name="Unknown USDA food",
            canonical_name="unknown usda food",
            protein=1,
            carbs=1,
            fat=1,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
        )

    def test_apply_usda_spanish_aliases_to_foods_creates_known_aliases(self):
        result = apply_usda_spanish_aliases_to_foods(
            foods=[self.oats, self.chicken, self.unknown],
        )

        self.assertEqual(result.matched_foods, 2)
        self.assertGreater(result.created_aliases, 0)
        self.assertEqual(result.skipped_aliases, 0)

        alias_names = {
            alias.name
            for alias in FoodAlias.objects.all()
        }

        self.assertIn("Avena", alias_names)
        self.assertIn("Pechuga de pollo", alias_names)

    def test_apply_usda_spanish_aliases_is_idempotent(self):
        first_result = apply_usda_spanish_aliases_to_foods(
            foods=[self.oats],
        )
        second_result = apply_usda_spanish_aliases_to_foods(
            foods=[self.oats],
        )

        self.assertGreater(first_result.created_aliases, 0)
        self.assertEqual(second_result.created_aliases, 0)
        self.assertGreater(second_result.skipped_aliases, 0)

    def test_apply_usda_spanish_aliases_to_visible_global_foods_ignores_hidden_foods(self):
        hidden_banana = Food.objects.create(
            name="Bananas, raw",
            canonical_name="bananas raw",
            protein=1.09,
            carbs=22.8,
            fat=0.33,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_HIDDEN,
        )

        result = apply_usda_spanish_aliases_to_visible_global_foods()

        self.assertEqual(result.matched_foods, 2)

        self.assertFalse(
            FoodAlias.objects.filter(
                food=hidden_banana,
                normalized_name="platano",
            ).exists()
        )