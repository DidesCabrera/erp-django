import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notas.domain.models import DailyPlan, DailyPlanMeal, Food, Meal, MealFood


User = get_user_model()


class DPMFoodPickerPayloadTests(TestCase):

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

        self.dailyplan = DailyPlan.objects.create(
            name="Plan 1",
            created_by=self.user,
            is_draft=False,
        )

        self.meal = Meal.objects.create(
            name="Meal snapshot",
            created_by=self.user,
            is_draft=False,
            is_public=False,
            is_forkable=True,
            is_copiable=False,
        )

        self.dpm = DailyPlanMeal.objects.create(
            dailyplan=self.dailyplan,
            meal=self.meal,
            order=1,
        )

    def test_dailyplanmeal_deepedit_includes_food_picker_payload_keys(self):
        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(
            reverse("dailyplanmeal_deepedit", args=[self.dailyplan.id, self.dpm.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("foods_json", response.context)
        self.assertIn("food_picker_json", response.context)

    def test_dailyplanmeal_deepedit_payloads_are_valid_json(self):
        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(
            reverse("dailyplanmeal_deepedit", args=[self.dailyplan.id, self.dpm.id])
        )

        foods_payload = json.loads(response.context["foods_json"])
        picker_context = json.loads(response.context["food_picker_json"])

        self.assertIsInstance(foods_payload, list)
        self.assertIsInstance(picker_context, dict)

    def test_dailyplanmeal_deepedit_foods_json_contains_available_foods(self):
        food_1 = Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )
        food_2 = Food.objects.create(
            name="Rice",
            protein=2,
            carbs=30,
            fat=1,
            created_by=self.user,
        )

        response = self.client.get(
            reverse("dailyplanmeal_deepedit", args=[self.dailyplan.id, self.dpm.id])
        )

        foods_payload = json.loads(response.context["foods_json"])
        serialized = json.dumps(foods_payload)

        self.assertIn(str(food_1.id), serialized)
        self.assertIn(str(food_2.id), serialized)
        self.assertIn("Egg", serialized)
        self.assertIn("Rice", serialized)

    def test_dailyplanmeal_deepedit_picker_context_is_add_mode_without_edit_food(self):
        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(
            reverse("dailyplanmeal_deepedit", args=[self.dailyplan.id, self.dpm.id])
        )

        picker_context = json.loads(response.context["food_picker_json"])

        self.assertEqual(picker_context["mode"], "add")
        self.assertIsNone(picker_context["editing"])

    def test_dailyplanmeal_deepedit_picker_context_is_edit_mode_with_edit_food(self):
        food = Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        meal_food = MealFood.objects.create(
            meal=self.meal,
            food=food,
            quantity=120,
        )

        response = self.client.get(
            reverse("dailyplanmeal_deepedit", args=[self.dailyplan.id, self.dpm.id])
            + f"?edit_food={meal_food.id}"
        )

        self.assertEqual(response.status_code, 200)

        picker_context = json.loads(response.context["food_picker_json"])

        self.assertEqual(picker_context["mode"], "edit")
        self.assertEqual(picker_context["editing"]["mealfood_id"], meal_food.id)
        self.assertEqual(picker_context["editing"]["food_id"], food.id)
        self.assertEqual(picker_context["editing"]["original_quantity"], 120.0)

    def test_dailyplanmeal_deepedit_post_save_food_creates_mealfood(self):
        food = Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.post(
            reverse("dailyplanmeal_deepedit", args=[self.dailyplan.id, self.dpm.id]),
            data={
                "save_food": "1",
                "food_id": food.id,
                "quantity": 100,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.meal.meal_food_set.count(), 1)

        meal_food = self.meal.meal_food_set.first()
        self.assertEqual(meal_food.food, food)
        self.assertEqual(meal_food.quantity, 100)

    def test_dailyplanmeal_deepedit_post_save_food_updates_existing_mealfood(self):
        food = Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        meal_food = MealFood.objects.create(
            meal=self.meal,
            food=food,
            quantity=100,
        )

        response = self.client.post(
            reverse("dailyplanmeal_deepedit", args=[self.dailyplan.id, self.dpm.id]),
            data={
                "save_food": "1",
                "mealfood_id": meal_food.id,
                "food_id": food.id,
                "quantity": 150,
            },
        )

        self.assertEqual(response.status_code, 200)

        meal_food.refresh_from_db()
        self.assertEqual(meal_food.quantity, 150)