import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notas.domain.models import Food, FoodAlias


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
            canonical_name="egg",
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

        self.assertIn("picker_source", item)
        self.assertIn("picker_label", item)
        self.assertIn("is_user_food", item)
        self.assertIn("is_global_food", item)
        self.assertIn("is_verified", item)
        self.assertIn("visibility", item)
        self.assertIn("data_quality_score", item)
        self.assertIn("source", item)
        self.assertIn("search_text", item)

    def test_foods_json_reflects_updated_food_values(self):
        food = Food.objects.create(
            name="Egg",
            canonical_name="egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        food.name = "Egg updated"
        food.canonical_name = "egg updated"
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

    def test_foods_json_is_ordered_by_name_for_user_foods(self):
        Food.objects.create(
            name="Rice",
            canonical_name="rice",
            protein=2,
            carbs=30,
            fat=1,
            created_by=self.user,
        )
        Food.objects.create(
            name="Egg",
            canonical_name="egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )
        Food.objects.create(
            name="Chicken",
            canonical_name="chicken",
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
            canonical_name="egg",
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
            canonical_name="egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIsNotNone(payload[0]["total_kcal"])

    def test_foods_json_includes_visible_global_foods(self):
        user_food = Food.objects.create(
            name="User Egg",
            canonical_name="user egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        global_food = Food.objects.create(
            name="Global Oats",
            canonical_name="global oats",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        names = [item["name"] for item in payload]

        self.assertIn(user_food.name, names)
        self.assertIn(global_food.name, names)

    def test_foods_json_excludes_private_foods_from_other_users(self):
        other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="12345678",
        )

        Food.objects.create(
            name="Other User Food",
            canonical_name="other user food",
            protein=1,
            carbs=1,
            fat=1,
            created_by=other_user,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        names = [item["name"] for item in payload]

        self.assertNotIn("Other User Food", names)

    def test_foods_json_excludes_hidden_global_foods(self):
        Food.objects.create(
            name="Hidden Global Banana",
            canonical_name="hidden global banana",
            protein=1,
            carbs=23,
            fat=0.3,
            created_by=None,
            is_global=True,
            is_active=True,
            visibility=Food.VISIBILITY_HIDDEN,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        names = [item["name"] for item in payload]

        self.assertNotIn("Hidden Global Banana", names)

    def test_foods_json_includes_picker_metadata(self):
        Food.objects.create(
            name="Global Oats",
            canonical_name="global oats",
            protein=16.9,
            carbs=66.3,
            fat=6.9,
            created_by=None,
            is_global=True,
            is_verified=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
            data_quality_score=90,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        item = next(
            food
            for food in payload
            if food["name"] == "Global Oats"
        )

        self.assertEqual(item["picker_source"], "global")
        self.assertEqual(item["picker_label"], "Global")
        self.assertFalse(item["is_user_food"])
        self.assertTrue(item["is_global_food"])
        self.assertTrue(item["is_verified"])
        self.assertEqual(item["visibility"], Food.VISIBILITY_CORE)
        self.assertEqual(item["data_quality_score"], 90)

    def test_foods_json_includes_search_text_for_user_food(self):
        Food.objects.create(
            name="Egg",
            canonical_name="egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        item = payload[0]

        self.assertIn("egg", item["search_text"])

    def test_foods_json_includes_search_text_for_alias_search(self):
        global_food = Food.objects.create(
            name="Chicken breast, cooked",
            canonical_name="chicken breast cooked",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=None,
            is_global=True,
            is_verified=True,
            is_active=True,
            visibility=Food.VISIBILITY_CORE,
            data_quality_score=90,
        )

        FoodAlias.objects.create(
            food=global_food,
            name="Pechuga de pollo",
            normalized_name="pechuga de pollo",
            language="es",
            country="CL",
        )

        response = self.client.get(reverse("foods_json"))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        item = next(
            food
            for food in payload
            if food["name"] == "Chicken breast, cooked"
        )

        self.assertIn("chicken breast cooked", item["search_text"])
        self.assertIn("pechuga de pollo", item["search_text"])
        self.assertIn("pollo", item["search_text"])