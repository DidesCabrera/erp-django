import json

from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.proposals.applicators import (
    AppliedProposalOperation,
    ProposalOperationsApplyResult,
    apply_validated_proposal_operations,
    validate_and_apply_proposal_operations,
)
from notas.application.proposals.validators import (
    validate_proposal_operations,
)
from notas.domain.models import (
    DailyPlan,
    DailyPlanMeal,
    Food,
    Meal,
    MealFood,
    NutritionProposal,
)


def assert_json_serializable(test_case, value):
    try:
        json.dumps(value)
    except TypeError as exc:
        test_case.fail(f"Value is not JSON serializable: {exc}")


class ProposalApplicatorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            email="felipe@example.com",
            password="pass123",
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

        self.mealfood = MealFood.objects.create(
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

        self.proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Apply quantity update",
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": self.mealfood.id,
                        "from_quantity": 100,
                        "to_quantity": 150,
                    }
                ],
            },
        )

    def test_apply_validated_update_meal_food_quantity_operation(self):
        operations = validate_proposal_operations(
            self.proposal,
        )

        result = apply_validated_proposal_operations(
            proposal=self.proposal,
            operations=operations,
        )

        self.mealfood.refresh_from_db()

        self.assertIsInstance(
            result,
            ProposalOperationsApplyResult,
        )
        self.assertEqual(result.proposal, self.proposal)
        self.assertEqual(result.applied_count, 1)
        self.assertEqual(self.mealfood.quantity, 150)

        applied_operation = result.applied_operations[0]

        self.assertIsInstance(
            applied_operation,
            AppliedProposalOperation,
        )
        self.assertEqual(
            applied_operation.type,
            "update_meal_food_quantity",
        )
        self.assertEqual(
            applied_operation.mealfood_id,
            self.mealfood.id,
        )
        self.assertEqual(
            applied_operation.meal_id,
            self.meal.id,
        )
        self.assertEqual(
            applied_operation.food_id,
            self.food.id,
        )
        self.assertEqual(
            applied_operation.food_name,
            "Base Food",
        )
        self.assertEqual(
            applied_operation.quantity_before,
            100,
        )
        self.assertEqual(
            applied_operation.quantity_after,
            150,
        )

        assert_json_serializable(
            self,
            applied_operation.as_dict(),
        )
        assert_json_serializable(
            self,
            result.as_dict(),
        )

    def test_validate_and_apply_proposal_operations(self):
        result = validate_and_apply_proposal_operations(
            self.proposal,
        )

        self.mealfood.refresh_from_db()

        self.assertEqual(result.applied_count, 1)
        self.assertEqual(self.mealfood.quantity, 150)

    def test_apply_empty_operations_is_safe_noop(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="No operation proposal",
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            },
        )

        result = validate_and_apply_proposal_operations(
            proposal,
        )

        self.mealfood.refresh_from_db()

        self.assertEqual(result.applied_count, 0)
        self.assertEqual(result.applied_operations, [])
        self.assertEqual(self.mealfood.quantity, 100)

        assert_json_serializable(
            self,
            result.as_dict(),
        )

    def test_validate_and_apply_reuses_validator_errors(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Invalid proposal",
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": self.mealfood.id,
                        "from_quantity": 80,
                        "to_quantity": 150,
                    }
                ],
            },
        )

        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_from_quantity_mismatch",
        ):
            validate_and_apply_proposal_operations(
                proposal,
            )

        self.mealfood.refresh_from_db()

        self.assertEqual(self.mealfood.quantity, 100)

    def test_apply_uses_existing_command_and_updates_meal_draft_status(self):
        draft_meal = Meal.objects.create(
            name="Draft Meal",
            created_by=self.user,
            is_public=False,
            is_draft=True,
        )

        draft_mealfood = MealFood.objects.create(
            meal=draft_meal,
            food=self.food,
            quantity=100,
            order=1,
        )

        draft_dailyplan = DailyPlan.objects.create(
            name="Draft Meal DailyPlan",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

        DailyPlanMeal.objects.create(
            dailyplan=draft_dailyplan,
            meal=draft_meal,
            order=1,
        )

        proposal = NutritionProposal.objects.create(
            dailyplan=draft_dailyplan,
            created_by=self.user,
            title="Apply on draft meal",
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": draft_mealfood.id,
                        "from_quantity": 100,
                        "to_quantity": 150,
                    }
                ],
            },
        )

        validate_and_apply_proposal_operations(
            proposal,
        )

        draft_mealfood.refresh_from_db()
        draft_meal.refresh_from_db()

        self.assertEqual(draft_mealfood.quantity, 150)
        self.assertFalse(draft_meal.is_draft)