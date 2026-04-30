from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.queries.meal_queries import (
    get_meal_detail,
    list_available_meals,
    list_user_meals,
    search_meals,
)
from notas.domain.models import Food, Meal, MealFood, MealShare


class MealQueryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            password="pass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="pass123",
        )

        self.egg = Food.objects.create(
            name="Egg",
            protein=13,
            carbs=1,
            fat=11,
            created_by=self.user,
        )

        self.rice = Food.objects.create(
            name="Rice",
            protein=2.7,
            carbs=28,
            fat=0.3,
            created_by=self.user,
        )

        self.user_meal = Meal.objects.create(
            name="Breakfast",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

        MealFood.objects.create(
            meal=self.user_meal,
            food=self.egg,
            quantity=100,
            order=1,
        )

        MealFood.objects.create(
            meal=self.user_meal,
            food=self.rice,
            quantity=200,
            order=2,
        )

        self.public_meal = Meal.objects.create(
            name="Public Meal",
            created_by=self.other_user,
            is_public=True,
            is_draft=False,
            is_forkable=True,
        )

        self.private_other_meal = Meal.objects.create(
            name="Private Other Meal",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
        )

        self.shared_meal = Meal.objects.create(
            name="Shared Meal",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
        )

        MealShare.objects.create(
            meal=self.shared_meal,
            sender=self.other_user,
            recipient_email="felipe@example.com",
            accepted_by=self.user,
        )

    def test_list_user_meals_returns_only_user_meals(self):
        meals = list_user_meals(self.user)

        names = [meal.name for meal in meals]

        self.assertEqual(names, ["Breakfast"])
        self.assertNotIn("Public Meal", names)
        self.assertNotIn("Private Other Meal", names)
        self.assertNotIn("Shared Meal", names)

    def test_list_available_meals_includes_public_and_shared(self):
        meals = list_available_meals(self.user)

        names = [meal.name for meal in meals]

        self.assertIn("Breakfast", names)
        self.assertIn("Public Meal", names)
        self.assertIn("Shared Meal", names)
        self.assertNotIn("Private Other Meal", names)

    def test_search_meals_filters_available_meals(self):
        meals = search_meals(self.user, "public")

        names = [meal.name for meal in meals]

        self.assertEqual(names, ["Public Meal"])

    def test_get_meal_detail_returns_serializable_dto(self):
        meal = get_meal_detail(
            self.user,
            self.user_meal.id,
        )

        data = meal.as_dict()

        self.assertEqual(data["id"], self.user_meal.id)
        self.assertEqual(data["name"], "Breakfast")
        self.assertEqual(data["foods_count"], 2)
        self.assertEqual(len(data["foods"]), 2)
        self.assertEqual(data["foods"][0]["food_name"], "Egg")
        self.assertEqual(data["foods"][0]["quantity"], 100.0)
        self.assertIn("total_kcal", data["kpis"])
        self.assertIn("alloc_protein", data["kpis"])

    def test_get_meal_detail_allows_public_meal(self):
        meal = get_meal_detail(
            self.user,
            self.public_meal.id,
        )

        self.assertEqual(meal.name, "Public Meal")

    def test_get_meal_detail_allows_shared_meal(self):
        meal = get_meal_detail(
            self.user,
            self.shared_meal.id,
        )

        self.assertEqual(meal.name, "Shared Meal")

    def test_get_meal_detail_blocks_private_other_meal(self):
        with self.assertRaises(Exception):
            get_meal_detail(
                self.user,
                self.private_other_meal.id,
            )