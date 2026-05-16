from django.test import TestCase

from notas.application.services.food_imports.localized_names import (
    FoodLocalizedNameInput,
    ensure_food_localized_names,
    get_primary_food_localized_name,
)
from notas.domain.models import Food, FoodLocalizedName


class FoodLocalizedNameServicesTests(TestCase):
    def setUp(self):
        self.food = Food.objects.create(
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

    def test_ensure_food_localized_names_creates_names(self):
        result = ensure_food_localized_names(
            food=self.food,
            localized_names=[
                FoodLocalizedNameInput(
                    name="Pechuga de pollo cocida",
                    language="es",
                    country="CL",
                    is_primary=True,
                ),
            ],
        )

        self.assertEqual(result.created_count, 1)
        self.assertEqual(result.updated_count, 0)
        self.assertEqual(result.skipped_count, 0)

        localized_name = FoodLocalizedName.objects.get()

        self.assertEqual(localized_name.food, self.food)
        self.assertEqual(localized_name.name, "Pechuga de pollo cocida")
        self.assertEqual(
            localized_name.normalized_name,
            "pechuga de pollo cocida",
        )
        self.assertEqual(localized_name.language, "es")
        self.assertEqual(localized_name.country, "CL")
        self.assertTrue(localized_name.is_primary)

    def test_ensure_food_localized_names_is_idempotent(self):
        localized_names = [
            FoodLocalizedNameInput(
                name="Pechuga de pollo cocida",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ]

        first_result = ensure_food_localized_names(
            food=self.food,
            localized_names=localized_names,
        )
        second_result = ensure_food_localized_names(
            food=self.food,
            localized_names=localized_names,
        )

        self.assertEqual(first_result.created_count, 1)
        self.assertEqual(second_result.created_count, 0)
        self.assertEqual(second_result.updated_count, 0)
        self.assertEqual(second_result.skipped_count, 1)
        self.assertEqual(FoodLocalizedName.objects.count(), 1)

    def test_ensure_food_localized_names_normalizes_language_and_country(self):
        ensure_food_localized_names(
            food=self.food,
            localized_names=[
                FoodLocalizedNameInput(
                    name="Pechuga de pollo cocida",
                    language="ES",
                    country="cl",
                    is_primary=True,
                ),
            ],
        )

        localized_name = FoodLocalizedName.objects.get()

        self.assertEqual(localized_name.language, "es")
        self.assertEqual(localized_name.country, "CL")

    def test_ensure_food_localized_names_skips_empty_names(self):
        result = ensure_food_localized_names(
            food=self.food,
            localized_names=[
                FoodLocalizedNameInput(name=""),
                FoodLocalizedNameInput(name="   "),
            ],
        )

        self.assertEqual(result.created_count, 0)
        self.assertEqual(result.updated_count, 0)
        self.assertEqual(result.skipped_count, 2)
        self.assertEqual(FoodLocalizedName.objects.count(), 0)

    def test_ensure_food_localized_names_updates_primary_flag(self):
        FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo cocida",
            normalized_name="pechuga de pollo cocida",
            language="es",
            country="CL",
            is_primary=False,
        )

        result = ensure_food_localized_names(
            food=self.food,
            localized_names=[
                FoodLocalizedNameInput(
                    name="Pechuga de pollo cocida",
                    language="es",
                    country="CL",
                    is_primary=True,
                ),
            ],
        )

        self.assertEqual(result.created_count, 0)
        self.assertEqual(result.updated_count, 1)
        self.assertEqual(result.skipped_count, 0)

        localized_name = FoodLocalizedName.objects.get()

        self.assertTrue(localized_name.is_primary)

    def test_get_primary_food_localized_name_returns_exact_country_match(self):
        FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo",
            normalized_name="pechuga de pollo",
            language="es",
            country="",
            is_primary=True,
        )
        FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo cocida",
            normalized_name="pechuga de pollo cocida",
            language="es",
            country="CL",
            is_primary=True,
        )

        display_name = get_primary_food_localized_name(
            food=self.food,
            language="es",
            country="CL",
        )

        self.assertEqual(display_name, "Pechuga de pollo cocida")

    def test_get_primary_food_localized_name_falls_back_to_language_only(self):
        FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo",
            normalized_name="pechuga de pollo",
            language="es",
            country="",
            is_primary=True,
        )

        display_name = get_primary_food_localized_name(
            food=self.food,
            language="es",
            country="CL",
        )

        self.assertEqual(display_name, "Pechuga de pollo")

    def test_get_primary_food_localized_name_returns_empty_string_without_match(self):
        display_name = get_primary_food_localized_name(
            food=self.food,
            language="es",
            country="CL",
        )

        self.assertEqual(display_name, "")
        