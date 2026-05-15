from django.test import TestCase

from notas.application.services.food_imports.aliases import (
    FoodAliasInput,
    ensure_food_aliases,
)
from notas.domain.models import Food, FoodAlias


class FoodAliasServicesTests(TestCase):
    def setUp(self):
        self.food = Food.objects.create(
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

    def test_ensure_food_aliases_creates_aliases(self):
        result = ensure_food_aliases(
            food=self.food,
            aliases=[
                FoodAliasInput(name="Avena", language="es", country="CL"),
                FoodAliasInput(name="Avena cruda", language="es", country="CL"),
            ],
        )

        self.assertEqual(result.created_count, 2)
        self.assertEqual(result.skipped_count, 0)
        self.assertEqual(FoodAlias.objects.count(), 2)

        aliases = {
            alias.normalized_name
            for alias in FoodAlias.objects.all()
        }

        self.assertIn("avena", aliases)
        self.assertIn("avena cruda", aliases)

    def test_ensure_food_aliases_is_idempotent(self):
        aliases = [
            FoodAliasInput(name="Avena", language="es", country="CL"),
        ]

        first_result = ensure_food_aliases(
            food=self.food,
            aliases=aliases,
        )
        second_result = ensure_food_aliases(
            food=self.food,
            aliases=aliases,
        )

        self.assertEqual(first_result.created_count, 1)
        self.assertEqual(second_result.created_count, 0)
        self.assertEqual(second_result.skipped_count, 1)
        self.assertEqual(FoodAlias.objects.count(), 1)

    def test_ensure_food_aliases_normalizes_language_and_country(self):
        ensure_food_aliases(
            food=self.food,
            aliases=[
                FoodAliasInput(name="Avena", language="ES", country="cl"),
            ],
        )

        alias = FoodAlias.objects.get()

        self.assertEqual(alias.language, "es")
        self.assertEqual(alias.country, "CL")

    def test_ensure_food_aliases_skips_empty_aliases(self):
        result = ensure_food_aliases(
            food=self.food,
            aliases=[
                FoodAliasInput(name=""),
                FoodAliasInput(name="   "),
            ],
        )

        self.assertEqual(result.created_count, 0)
        self.assertEqual(result.skipped_count, 2)
        self.assertEqual(FoodAlias.objects.count(), 0)