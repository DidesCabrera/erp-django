from django.test import TestCase

from notas.domain.models import DailyPlan, Meal
from notas.presentation.composition.js.dpm_food_picker_builder import (
    build_dpm_food_picker_context_payload,
)
from notas.presentation.frontend.jscontext.dpm_food_picker import (
    DpmFoodPickerContextPayload,
)


class DpmFoodPickerBuilderContractTests(TestCase):

    def test_builder_returns_payload_object_in_add_mode(self):
        meal = Meal(id=1)
        dailyplan = DailyPlan(id=2)

        payload = build_dpm_food_picker_context_payload(
            meal=meal,
            meal_kpis={"total_kcal": 100},
            dailyplan=dailyplan,
            dailyplan_kpis={"total_kcal": 500},
            mealfood=None,
        )

        self.assertIsInstance(payload, DpmFoodPickerContextPayload)
        self.assertEqual(payload.mode, "add")
        self.assertIsNone(payload.editing)

    def test_builder_returns_payload_object_in_edit_mode(self):
        class MealFoodStub:
            id = 10
            food_id = 20
            quantity = 150

        meal = Meal(id=1)
        dailyplan = DailyPlan(id=2)

        payload = build_dpm_food_picker_context_payload(
            meal=meal,
            meal_kpis={"total_kcal": 100},
            dailyplan=dailyplan,
            dailyplan_kpis={"total_kcal": 500},
            mealfood=MealFoodStub(),
        )

        self.assertIsInstance(payload, DpmFoodPickerContextPayload)
        self.assertEqual(payload.mode, "edit")
        self.assertEqual(payload.editing["mealfood_id"], 10)