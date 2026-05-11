from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from notas.application.ai_tools.read_tools import list_food_catalog_tool
from notas.domain.models import Food


class AIFoodCatalogToolTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            password="pass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="pass123",
        )

        self.system_food = Food.objects.create(
            name="Plátano",
            protein=1.1,
            carbs=23,
            fat=0.3,
            created_by=None,
        )
        self.user_food = Food.objects.create(
            name="Pechuga pollo",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=self.user,
        )
        self.other_food = Food.objects.create(
            name="Private Other Food",
            protein=100,
            carbs=100,
            fat=100,
            created_by=self.other_user,
        )

    def test_list_food_catalog_tool_returns_readable_catalog(self):
        result = list_food_catalog_tool(
            user=self.user,
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertIsNone(data["error"])

        foods = data["data"]["catalog"]["foods"]
        names = {
            food["name"]
            for food in foods
        }

        self.assertIn("Plátano", names)
        self.assertIn("Pechuga pollo", names)
        self.assertNotIn("Private Other Food", names)

    def test_list_food_catalog_tool_filters_by_search(self):
        result = list_food_catalog_tool(
            user=self.user,
            search="pechuga",
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(data["data"]["catalog"]["count"], 1)
        self.assertEqual(
            data["data"]["catalog"]["foods"][0]["name"],
            "Pechuga pollo",
        )

    def test_list_food_catalog_tool_requires_authenticated_user(self):
        result = list_food_catalog_tool(
            user=AnonymousUser(),
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(data["data"], {})
        self.assertIsNotNone(data["error"])