from django.test import SimpleTestCase

from notas.application.services.food_imports.visibility_policy import (
    resolve_initial_food_visibility,
)
from notas.domain.models import Food


class FoodImportVisibilityPolicyTests(SimpleTestCase):
    def test_high_quality_imported_food_starts_as_extended(self):
        visibility = resolve_initial_food_visibility(
            quality_score=80,
        )

        self.assertEqual(visibility, Food.VISIBILITY_EXTENDED)

    def test_borderline_quality_imported_food_starts_as_extended(self):
        visibility = resolve_initial_food_visibility(
            quality_score=70,
        )

        self.assertEqual(visibility, Food.VISIBILITY_EXTENDED)

    def test_low_quality_imported_food_starts_as_hidden(self):
        visibility = resolve_initial_food_visibility(
            quality_score=60,
        )

        self.assertEqual(visibility, Food.VISIBILITY_HIDDEN)

    def test_imported_food_is_never_core_by_default(self):
        visibility = resolve_initial_food_visibility(
            quality_score=100,
        )

        self.assertNotEqual(visibility, Food.VISIBILITY_CORE)