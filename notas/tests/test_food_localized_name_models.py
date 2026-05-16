from django.db import IntegrityError
from django.test import TestCase

from notas.domain.models import Food, FoodLocalizedName


class FoodLocalizedNameModelTests(TestCase):
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

    def test_food_localized_name_can_be_created(self):
        localized_name = FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo cocida",
            normalized_name="pechuga de pollo cocida",
            language="es",
            country="CL",
            is_primary=True,
        )

        self.assertEqual(localized_name.food, self.food)
        self.assertEqual(localized_name.name, "Pechuga de pollo cocida")
        self.assertEqual(localized_name.normalized_name, "pechuga de pollo cocida")
        self.assertEqual(localized_name.language, "es")
        self.assertEqual(localized_name.country, "CL")
        self.assertTrue(localized_name.is_primary)

    def test_food_localized_name_is_related_to_food(self):
        FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo cocida",
            normalized_name="pechuga de pollo cocida",
            language="es",
            country="CL",
            is_primary=True,
        )

        self.assertEqual(self.food.localized_names.count(), 1)
        self.assertEqual(
            self.food.localized_names.first().name,
            "Pechuga de pollo cocida",
        )

    def test_food_localized_name_unique_constraint(self):
        FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo cocida",
            normalized_name="pechuga de pollo cocida",
            language="es",
            country="CL",
            is_primary=True,
        )

        with self.assertRaises(IntegrityError):
            FoodLocalizedName.objects.create(
                food=self.food,
                name="Pechuga de pollo cocida",
                normalized_name="pechuga de pollo cocida",
                language="es",
                country="CL",
                is_primary=True,
            )

    def test_same_localized_name_can_exist_for_different_country(self):
        FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo cocida",
            normalized_name="pechuga de pollo cocida",
            language="es",
            country="CL",
            is_primary=True,
        )

        localized_name = FoodLocalizedName.objects.create(
            food=self.food,
            name="Pechuga de pollo cocida",
            normalized_name="pechuga de pollo cocida",
            language="es",
            country="AR",
            is_primary=True,
        )

        self.assertEqual(localized_name.country, "AR")
        self.assertEqual(FoodLocalizedName.objects.count(), 2)