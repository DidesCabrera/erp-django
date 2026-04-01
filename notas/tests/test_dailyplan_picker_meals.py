import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notas.domain.models import DailyPlan, DailyPlanMeal, Meal


User = get_user_model()


class DailyPlanMealPickerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@test.com",
            password="12345678",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
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

    def test_dailyplan_edit_picker_should_only_include_library_meals_of_current_user(self):
        library_meal = Meal.objects.create(
            name="Library meal",
            created_by=self.user,
            is_draft=False,
            is_public=False,
            is_forkable=True,
            is_copiable=False,
        )

        draft_meal = Meal.objects.create(
            name="Draft meal",
            created_by=self.user,
            is_draft=True,
            is_public=False,
            is_forkable=True,
            is_copiable=False,
        )

        dpm_meal = Meal.objects.create(
            name="DPM meal",
            created_by=self.user,
            is_draft=False,
            is_public=False,
            is_forkable=True,
            is_copiable=False,
        )

        DailyPlanMeal.objects.create(
            dailyplan=self.dailyplan,
            meal=dpm_meal,
            order=1,
        )

        other_user_meal = Meal.objects.create(
            name="Other user meal",
            created_by=self.other_user,
            is_draft=False,
            is_public=False,
            is_forkable=True,
            is_copiable=False,
        )

        response = self.client.get(
            reverse("dailyplan_edit", args=[self.dailyplan.id])
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn("meals_json", response.context)

        meals_payload = json.loads(response.context["meals_json"])
        serialized = json.dumps(meals_payload)

        self.assertIn("Library meal", serialized)

        self.assertNotIn("Draft meal", serialized)
        self.assertNotIn("DPM meal", serialized)
        self.assertNotIn("Other user meal", serialized)

    def test_dailyplan_edit_picker_payload_is_valid_json_list(self):
        Meal.objects.create(
            name="Library meal",
            created_by=self.user,
            is_draft=False,
            is_public=False,
            is_forkable=True,
            is_copiable=False,
        )

        response = self.client.get(
            reverse("dailyplan_edit", args=[self.dailyplan.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("meals_json", response.context)

        meals_payload = json.loads(response.context["meals_json"])

        self.assertIsInstance(meals_payload, list)

    def test_dailyplan_edit_picker_includes_current_user_library_meal_id(self):
        meal = Meal.objects.create(
            name="Visible meal",
            created_by=self.user,
            is_draft=False,
            is_public=False,
            is_forkable=True,
            is_copiable=False,
        )

        response = self.client.get(
            reverse("dailyplan_edit", args=[self.dailyplan.id])
        )

        self.assertEqual(response.status_code, 200)

        meals_payload = json.loads(response.context["meals_json"])
        serialized = json.dumps(meals_payload)

        self.assertIn(str(meal.id), serialized)
        self.assertIn("Visible meal", serialized)