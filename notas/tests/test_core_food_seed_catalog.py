from django.test import SimpleTestCase

from notas.application.services.food_imports.core_food_seed_catalog import (
    CORE_FOOD_SEED_CATALOG,
    get_core_food_seed_by_canonical_name,
    get_core_food_seed_canonical_names,
)


class CoreFoodSeedCatalogTests(SimpleTestCase):
    def test_core_food_seed_catalog_has_expected_initial_foods(self):
        canonical_names = get_core_food_seed_canonical_names()

        self.assertIn("oats raw", canonical_names)
        self.assertIn("chicken breast cooked", canonical_names)
        self.assertIn("rice white cooked", canonical_names)
        self.assertIn("bananas raw", canonical_names)

    def test_core_food_seed_catalog_items_have_localized_names(self):
        for item in CORE_FOOD_SEED_CATALOG:
            self.assertTrue(item.localized_names)
            self.assertTrue(item.localized_names[0].name)
            self.assertTrue(item.localized_names[0].is_primary)

    def test_core_food_seed_catalog_items_have_aliases(self):
        for item in CORE_FOOD_SEED_CATALOG:
            self.assertTrue(item.aliases)

    def test_get_core_food_seed_by_canonical_name_returns_index(self):
        index = get_core_food_seed_by_canonical_name()

        self.assertIn("oats raw", index)
        self.assertEqual(
            index["oats raw"].localized_names[0].name,
            "Avena",
        )
        self.assertEqual(
            index["chicken breast cooked"].localized_names[0].name,
            "Pechuga de pollo cocida",
        )