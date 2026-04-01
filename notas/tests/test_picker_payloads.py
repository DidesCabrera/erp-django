import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notas.domain.models import DailyPlan, Food, Meal, MealFood


User = get_user_model()


class PickerPayloadTests(TestCase):

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

    def test_meal_edit_includes_picker_payload_keys(self):
        meal = Meal.objects.create(
            name="Editable meal",
            created_by=self.user,
            is_draft=True,
        )

        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(
            reverse("meal_edit", args=[meal.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("foods_json", response.context)
        self.assertIn("food_picker_context", response.context)
        self.assertIn("show_return_to_dailyplan", response.context)

    def test_meal_edit_picker_payloads_are_valid_json(self):
        meal = Meal.objects.create(
            name="Editable meal",
            created_by=self.user,
            is_draft=True,
        )

        Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        response = self.client.get(
            reverse("meal_edit", args=[meal.id])
        )

        foods_json = response.context["foods_json"]
        picker_context_json = response.context["food_picker_context"]

        foods_payload = json.loads(foods_json)
        picker_context = json.loads(picker_context_json)

        self.assertIsInstance(foods_payload, list)
        self.assertIsInstance(picker_context, dict)

    def test_meal_edit_foods_json_contains_available_foods(self):
        meal = Meal.objects.create(
            name="Editable meal",
            created_by=self.user,
            is_draft=True,
        )

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
            reverse("meal_edit", args=[meal.id])
        )

        foods_payload = json.loads(response.context["foods_json"])

        self.assertEqual(len(foods_payload), 2)

        serialized = json.dumps(foods_payload)
        self.assertIn(str(food_1.id), serialized)
        self.assertIn(str(food_2.id), serialized)
        self.assertIn("Egg", serialized)
        self.assertIn("Rice", serialized)

    def test_meal_edit_show_return_to_dailyplan_is_false_without_pending_dailyplan(self):
        meal = Meal.objects.create(
            name="Editable meal",
            created_by=self.user,
            is_draft=False,
        )

        response = self.client.get(
            reverse("meal_edit", args=[meal.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["show_return_to_dailyplan"])

    def test_meal_edit_show_return_to_dailyplan_is_true_with_pending_dailyplan_and_not_draft(self):
        dailyplan = DailyPlan.objects.create(
            name="Plan 1",
            created_by=self.user,
            is_draft=False,
        )

        meal = Meal.objects.create(
            name="Meal from plan",
            created_by=self.user,
            is_draft=False,
            pending_dailyplan=dailyplan,
        )

        response = self.client.get(
            reverse("meal_edit", args=[meal.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["show_return_to_dailyplan"])

    def test_meal_edit_show_return_to_dailyplan_is_false_when_meal_is_still_draft(self):
        dailyplan = DailyPlan.objects.create(
            name="Plan 1",
            created_by=self.user,
            is_draft=False,
        )

        meal = Meal.objects.create(
            name="Draft meal from plan",
            created_by=self.user,
            is_draft=True,
            pending_dailyplan=dailyplan,
        )

        response = self.client.get(
            reverse("meal_edit", args=[meal.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["show_return_to_dailyplan"])

    def test_meal_edit_with_edit_food_param_loads_picker_context_successfully(self):
        meal = Meal.objects.create(
            name="Editable meal",
            created_by=self.user,
            is_draft=False,
        )

        food = Food.objects.create(
            name="Egg",
            protein=10,
            carbs=2,
            fat=5,
            created_by=self.user,
        )

        meal_food = MealFood.objects.create(
            meal=meal,
            food=food,
            quantity=120,
        )

        response = self.client.get(
            reverse("meal_edit", args=[meal.id]) + f"?edit_food={meal_food.id}"
        )

        self.assertEqual(response.status_code, 200)

        picker_context = json.loads(response.context["food_picker_context"])

        self.assertEqual(picker_context["mode"], "edit")
        self.assertEqual(picker_context["editing"]["mealfood_id"], meal_food.id)
        self.assertEqual(picker_context["editing"]["food_id"], food.id)
        self.assertEqual(picker_context["editing"]["original_quantity"], 120.0)