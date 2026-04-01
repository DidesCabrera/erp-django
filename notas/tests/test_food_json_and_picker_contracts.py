import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notas.domain.models import Food


User = get_user_model()


class FoodJsonAndPickerContractTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@test.com",
            password="12345678",
        )

        self.client = Client()
        self.client.login(
            username="felipe",
            password="12345678",
        )

    def test_foods_json_returns_expected_keys_per_item(self):
        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(len(payload), 1)

        item = payload[0]

        self.assertIn("id", item)
        self.assertIn("name", item)
        self.assertIn("protein", item)
        self.assertIn("carbs", item)
        self.assertIn("fat", item)
        self.assertIn("total_kcal", item)
        self.assertIn("alloc", item)

    def test_foods_json_reflects_updated_food_values(self):
        food = Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        food.name = "Egg updated"
        food.protein = 12
        food.carbs = 3
        food.fat = 6
        food.save()

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(len(payload), 1)

        item = payload[0]
        self.assertEqual(item["id"], food.id)
        self.assertEqual(item["name"], "Egg updated")
        self.assertEqual(item["protein"], 12)
        self.assertEqual(item["carbs"], 3)
        self.assertEqual(item["fat"], 6)

    def test_foods_json_is_ordered_by_name(self):
        Food.objects.create(
            name="Rice",
            protein=2,
            carbs=30,
            fat=1,
            created_by=self.user,
        )
        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )
        Food.objects.create(
            name="Chicken",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=self.user,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        names = [item["name"] for item in payload]

        self.assertEqual(names, ["Chicken", "Egg", "Rice"])

    def test_foods_json_alloc_contains_expected_keys(self):
        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        alloc = payload[0]["alloc"]

        self.assertIn("protein", alloc)
        self.assertIn("carbs", alloc)
        self.assertIn("fat", alloc)

    def test_foods_json_total_kcal_is_present(self):
        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIsNotNone(payload[0]["total_kcal"])