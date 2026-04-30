from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.queries.validation_queries import (
    compare_dailyplan_to_targets,
)
from notas.domain.models import (
    DailyPlan,
    DailyPlanMeal,
    Food,
    Meal,
    MealFood,
    WeightLog,
)


class ValidationQueryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            password="pass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="pass123",
        )

        WeightLog.objects.create(
            user=self.user,
            date=date.today(),
            weight_kg=100,
        )

        self.food = Food.objects.create(
            name="Base Food",
            protein=10,
            carbs=20,
            fat=0,
            created_by=self.user,
        )

        self.meal = Meal.objects.create(
            name="Base Meal",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

        MealFood.objects.create(
            meal=self.meal,
            food=self.food,
            quantity=100,
            order=1,
        )

        self.dailyplan = DailyPlan.objects.create(
            name="Training Day",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

        DailyPlanMeal.objects.create(
            dailyplan=self.dailyplan,
            meal=self.meal,
            order=1,
        )

        self.private_other_dailyplan = DailyPlan.objects.create(
            name="Private Other Plan",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
        )

    def test_compare_dailyplan_to_targets_returns_serializable_summary(self):
        summary = compare_dailyplan_to_targets(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            targets={
                "total_kcal": 120,
                "protein": 10,
                "carbs": 20,
                "fat": 0,
                "ppk": 0.1,
            },
        )

        data = summary.as_dict()

        self.assertEqual(data["dailyplan_id"], self.dailyplan.id)
        self.assertEqual(data["dailyplan_name"], "Training Day")
        self.assertTrue(data["within_tolerance"])

        self.assertEqual(data["actual"]["total_kcal"], 120)
        self.assertEqual(data["actual"]["protein"], 10)
        self.assertEqual(data["actual"]["carbs"], 20)
        self.assertEqual(data["actual"]["fat"], 0)
        self.assertEqual(data["actual"]["ppk"], 0.1)

        self.assertEqual(len(data["metrics"]), 5)

    def test_compare_dailyplan_to_targets_detects_under_target_metric(self):
        summary = compare_dailyplan_to_targets(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            targets={
                "protein": 30,
            },
            tolerances={
                "protein": 5,
            },
        )

        data = summary.as_dict()

        self.assertFalse(data["within_tolerance"])
        self.assertEqual(data["delta"]["protein"], -20)
        self.assertEqual(data["metrics"][0]["status"], "under_target")
        self.assertFalse(data["metrics"][0]["within_tolerance"])

    def test_compare_dailyplan_to_targets_detects_over_target_metric(self):
        summary = compare_dailyplan_to_targets(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            targets={
                "total_kcal": 50,
            },
            tolerances={
                "total_kcal": 10,
            },
        )

        data = summary.as_dict()

        self.assertFalse(data["within_tolerance"])
        self.assertEqual(data["delta"]["total_kcal"], 70)
        self.assertEqual(data["metrics"][0]["status"], "over_target")

    def test_compare_dailyplan_to_targets_uses_default_tolerances(self):
        summary = compare_dailyplan_to_targets(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            targets={
                "total_kcal": 200,
            },
        )

        data = summary.as_dict()

        self.assertTrue(data["within_tolerance"])
        self.assertEqual(data["delta"]["total_kcal"], -80)
        self.assertEqual(data["tolerances"]["total_kcal"], 100)

    def test_compare_dailyplan_to_targets_rejects_unknown_metric(self):
        with self.assertRaises(ValueError):
            compare_dailyplan_to_targets(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                targets={
                    "fiber": 30,
                },
            )

    def test_compare_dailyplan_to_targets_respects_dailyplan_access(self):
        with self.assertRaises(Exception):
            compare_dailyplan_to_targets(
                user=self.user,
                dailyplan_id=self.private_other_dailyplan.id,
                targets={
                    "protein": 10,
                },
            )