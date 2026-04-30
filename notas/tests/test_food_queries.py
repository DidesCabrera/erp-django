from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.queries.food_queries import (
    get_food_detail,
    list_available_foods,
    list_user_foods,
    search_foods,
)
from notas.domain.models import Food


class FoodQueryTests(TestCase):
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

        self.other_food = Food.objects.create(
            name="Private Other Food",
            protein=1,
            carbs=2,
            fat=3,
            created_by=self.other_user,
        )

        self.system_food = Food.objects.create(
            name="System Chicken",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=None,
        )

    def test_list_user_foods_returns_only_user_foods(self):
        foods = list_user_foods(self.user)

        names = [food.name for food in foods]

        self.assertEqual(names, ["Egg", "Rice"])
        self.assertNotIn("Private Other Food", names)
        self.assertNotIn("System Chicken", names)

    def test_list_available_foods_includes_user_and_system_foods(self):
        foods = list_available_foods(self.user)

        names = [food.name for food in foods]

        self.assertIn("Egg", names)
        self.assertIn("Rice", names)
        self.assertIn("System Chicken", names)
        self.assertNotIn("Private Other Food", names)

    def test_search_foods_filters_available_foods_by_name(self):
        foods = search_foods(self.user, "chicken")

        names = [food.name for food in foods]

        self.assertEqual(names, ["System Chicken"])

    def test_get_food_detail_returns_serializable_dto(self):
        food = get_food_detail(self.user, self.egg.id)

        data = food.as_dict()

        self.assertEqual(data["id"], self.egg.id)
        self.assertEqual(data["name"], "Egg")
        self.assertEqual(data["category"], "user")
        self.assertEqual(data["created_by_id"], self.user.id)
        self.assertEqual(data["macros"]["protein"], 13.0)
        self.assertIn("total_kcal", data["macros"])
        self.assertIn("alloc_protein", data["macros"])

    def test_get_food_detail_allows_system_food(self):
        food = get_food_detail(self.user, self.system_food.id)

        self.assertEqual(food.name, "System Chicken")
        self.assertEqual(food.category, "system")

    def test_get_food_detail_does_not_allow_other_users_private_food(self):
        with self.assertRaises(Exception):
            get_food_detail(self.user, self.other_food.id)