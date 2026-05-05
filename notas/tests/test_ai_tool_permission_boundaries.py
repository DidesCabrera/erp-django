import json
from datetime import date

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from notas.application.ai_tools.proposal_tools import (
    create_validated_dailyplan_proposal_tool,
)
from notas.application.ai_tools.read_tools import (
    read_dailyplan_tool,
    read_food_tool,
    read_meal_tool,
    read_proposal_tool,
)
from notas.application.ai_tools.validation_tools import (
    compare_dailyplan_to_targets_tool,
)
from notas.domain.models import (
    DailyPlan,
    DailyPlanMeal,
    Food,
    Meal,
    MealFood,
    NutritionProposal,
    WeightLog,
)


def assert_json_serializable(test_case, value):
    try:
        json.dumps(value)
    except TypeError as exc:
        test_case.fail(f"Value is not JSON serializable: {exc}")


class AIToolPermissionBoundaryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
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
        self.other_food = Food.objects.create(
            name="Other Private Food",
            protein=1,
            carbs=1,
            fat=1,
            created_by=self.other_user,
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

        self.other_meal = Meal.objects.create(
            name="Other Private Meal",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
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

        self.other_dailyplan = DailyPlan.objects.create(
            name="Other Private DailyPlan",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
        )

        self.proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="User proposal",
        )
        self.other_proposal = NutritionProposal.objects.create(
            dailyplan=self.other_dailyplan,
            created_by=self.other_user,
            title="Other private proposal",
        )

    def assert_tool_error(self, result, code: str):
        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            code,
        )

        assert_json_serializable(
            self,
            data,
        )

    def test_read_tools_require_user(self):
        tools = [
            lambda: read_food_tool(None, self.food.id),
            lambda: read_meal_tool(None, self.meal.id),
            lambda: read_dailyplan_tool(None, self.dailyplan.id),
            lambda: read_proposal_tool(None, self.proposal.id),
        ]

        for run_tool in tools:
            self.assert_tool_error(
                run_tool(),
                "tool_user_required",
            )

    def test_read_tools_reject_anonymous_user(self):
        anonymous_user = AnonymousUser()

        tools = [
            lambda: read_food_tool(anonymous_user, self.food.id),
            lambda: read_meal_tool(anonymous_user, self.meal.id),
            lambda: read_dailyplan_tool(anonymous_user, self.dailyplan.id),
            lambda: read_proposal_tool(anonymous_user, self.proposal.id),
        ]

        for run_tool in tools:
            self.assert_tool_error(
                run_tool(),
                "tool_user_not_authenticated",
            )

    def test_read_tools_do_not_expose_private_resources(self):
        checks = [
            (
                read_food_tool(
                    self.user,
                    self.other_food.id,
                ),
                "not_found",
            ),
            (
                read_meal_tool(
                    self.user,
                    self.other_meal.id,
                ),
                "not_found",
            ),
            (
                read_dailyplan_tool(
                    self.user,
                    self.other_dailyplan.id,
                ),
                "not_found",
            ),
            (
                read_proposal_tool(
                    self.user,
                    self.other_proposal.id,
                ),
                "not_found",
            ),
        ]

        for result, code in checks:
            self.assert_tool_error(
                result,
                code,
            )

    def test_validation_tool_requires_user(self):
        result = compare_dailyplan_to_targets_tool(
            user=None,
            dailyplan_id=self.dailyplan.id,
            targets={
                "protein": 30,
            },
        )

        self.assert_tool_error(
            result,
            "tool_user_required",
        )

    def test_validation_tool_rejects_anonymous_user(self):
        result = compare_dailyplan_to_targets_tool(
            user=AnonymousUser(),
            dailyplan_id=self.dailyplan.id,
            targets={
                "protein": 30,
            },
        )

        self.assert_tool_error(
            result,
            "tool_user_not_authenticated",
        )

    def test_validation_tool_does_not_expose_private_dailyplan(self):
        result = compare_dailyplan_to_targets_tool(
            user=self.user,
            dailyplan_id=self.other_dailyplan.id,
            targets={
                "protein": 30,
            },
        )

        self.assert_tool_error(
            result,
            "not_found",
        )

    def test_proposal_tool_requires_user(self):
        result = create_validated_dailyplan_proposal_tool(
            user=None,
            dailyplan_id=self.dailyplan.id,
            title="AI proposal",
            targets={
                "protein": 30,
            },
        )

        self.assert_tool_error(
            result,
            "tool_user_required",
        )

    def test_proposal_tool_rejects_anonymous_user(self):
        result = create_validated_dailyplan_proposal_tool(
            user=AnonymousUser(),
            dailyplan_id=self.dailyplan.id,
            title="AI proposal",
            targets={
                "protein": 30,
            },
        )

        self.assert_tool_error(
            result,
            "tool_user_not_authenticated",
        )

    def test_proposal_tool_does_not_create_for_private_other_dailyplan(self):
        result = create_validated_dailyplan_proposal_tool(
            user=self.user,
            dailyplan_id=self.other_dailyplan.id,
            title="AI proposal",
            targets={
                "protein": 30,
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertIn(
            data["error"]["code"],
            {
                "not_found",
                "dailyplan_not_available_for_proposal",
            },
        )
        self.assertFalse(
            NutritionProposal.objects.filter(
                dailyplan=self.other_dailyplan,
                created_by=self.user,
            ).exists()
        )

        assert_json_serializable(
            self,
            data,
        )