from django.test import TestCase

from notas.application.services.food_imports.usda.spanish_display_names import (
    apply_usda_spanish_display_names_to_foods,
    apply_usda_spanish_display_names_to_visible_global_foods,
    translate_usda_food_name_to_spanish,
)
from notas.domain.models import Food, FoodLocalizedName, FoodSourceMetadata


class USDASpanishDisplayNamesTests(TestCase):
    def setUp(self):
        self.chicken = self._create_usda_food(
            name="Chicken, drumstick, meat and skin, raw",
            canonical_name="chicken drumstick meat and skin raw",
            source_food_id="2727566",
        )

        self.beans = self._create_usda_food(
            name="Beans, snap, green, canned, regular pack, drained solids",
            canonical_name="beans snap green canned regular pack drained solids",
            source_food_id="321611",
        )

        self.core_oats = self._create_usda_food(
            name="Oats, raw",
            canonical_name="oats raw",
            source_food_id="1001",
            visibility=Food.VISIBILITY_CORE,
        )

        FoodLocalizedName.objects.create(
            food=self.core_oats,
            name="Avena",
            normalized_name="avena",
            language="es",
            country="CL",
            is_primary=True,
        )

        self.hidden_food = self._create_usda_food(
            name="Hidden USDA food",
            canonical_name="hidden usda food",
            source_food_id="9999",
            visibility=Food.VISIBILITY_HIDDEN,
        )

    def test_translate_usda_food_name_to_spanish_uses_exact_core_translation(self):
        self.assertEqual(
            translate_usda_food_name_to_spanish("Oats, raw"),
            "Avena",
        )

    def test_translate_usda_food_name_to_spanish_translates_common_usda_parts(self):
        self.assertEqual(
            translate_usda_food_name_to_spanish(
                "Chicken, drumstick, meat and skin, raw"
            ),
            "Pollo, Trutro corto, carne y piel, crudo",
        )

        self.assertEqual(
            translate_usda_food_name_to_spanish(
                "Beans, snap, green, canned, regular pack, drained solids"
            ),
            "Porotos, Snap, verde, enlatado, envase regular, sólidos drenados",
        )

    def test_apply_usda_spanish_display_names_to_foods_creates_localized_names(self):
        result = apply_usda_spanish_display_names_to_foods(
            foods=[self.chicken, self.beans],
        )

        self.assertEqual(result.matched_foods, 2)
        self.assertEqual(result.created_localized_names, 2)
        self.assertEqual(result.updated_localized_names, 0)
        self.assertEqual(result.skipped_localized_names, 0)

        self.assertTrue(
            FoodLocalizedName.objects.filter(
                food=self.chicken,
                language="es",
                country="CL",
                is_primary=True,
            ).exists()
        )

        self.assertTrue(
            FoodLocalizedName.objects.filter(
                food=self.beans,
                language="es",
                country="CL",
                is_primary=True,
            ).exists()
        )

    def test_apply_usda_spanish_display_names_preserves_existing_primary_name(self):
        result = apply_usda_spanish_display_names_to_foods(
            foods=[self.core_oats],
        )

        self.assertEqual(result.matched_foods, 1)
        self.assertEqual(result.created_localized_names, 0)
        self.assertEqual(result.skipped_localized_names, 1)

        localized_name = FoodLocalizedName.objects.get(food=self.core_oats)

        self.assertEqual(localized_name.name, "Avena")

    def test_apply_usda_spanish_display_names_is_idempotent(self):
        first_result = apply_usda_spanish_display_names_to_foods(
            foods=[self.chicken],
        )
        second_result = apply_usda_spanish_display_names_to_foods(
            foods=[self.chicken],
        )

        self.assertEqual(first_result.created_localized_names, 1)
        self.assertEqual(second_result.created_localized_names, 0)
        self.assertEqual(second_result.skipped_localized_names, 1)

        self.assertEqual(
            FoodLocalizedName.objects.filter(food=self.chicken).count(),
            1,
        )

    def test_apply_usda_spanish_display_names_to_visible_global_foods_ignores_hidden_foods(self):
        result = apply_usda_spanish_display_names_to_visible_global_foods()

        self.assertEqual(result.matched_foods, 3)

        self.assertFalse(
            FoodLocalizedName.objects.filter(
                food=self.hidden_food,
                language="es",
                country="CL",
            ).exists()
        )

    def _create_usda_food(
        self,
        *,
        name,
        canonical_name,
        source_food_id,
        visibility=Food.VISIBILITY_EXTENDED,
    ):
        food = Food.objects.create(
            name=name,
            canonical_name=canonical_name,
            protein=10,
            carbs=10,
            fat=10,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=visibility,
            data_quality_score=75,
        )

        FoodSourceMetadata.objects.create(
            food=food,
            source=FoodSourceMetadata.SOURCE_USDA,
            source_food_id=source_food_id,
            source_dataset="foundation_foods",
            source_version="2026-04",
        )

        return food