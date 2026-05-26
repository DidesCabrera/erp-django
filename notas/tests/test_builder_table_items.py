from django.contrib.auth import get_user_model
from django.test import TestCase

from notas.domain.models import Food, FoodLocalizedName, Meal, MealFood
from notas.presentation.composition.viewmodel.components.builder_table_items import (
    build_mealfood_table_item,
)


User = get_user_model()


class BuilderTableItemsTests(TestCase):
    def test_build_mealfood_table_item_uses_food_display_name(self):
        user = User.objects.create_user(
            username="felipe",
            email="felipe@test.com",
            password="12345678",
        )

        meal = Meal.objects.create(
            name="Meal test",
            created_by=user,
        )

        food = Food.objects.create(
            name="Oats, raw",
            canonical_name="oats raw",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
            data_quality_score=90,
        )

        FoodLocalizedName.objects.create(
            food=food,
            name="Avena",
            normalized_name="avena",
            language="es",
            country="CL",
            is_primary=True,
        )

        meal_food = MealFood.objects.create(
            meal=meal,
            food=food,
            quantity=100,
        )

        item = build_mealfood_table_item(meal_food)

        self.assertEqual(item["rel"]["name"], "Avena")
        self.assertEqual(item["rel"]["quantity_unit"], "g")