import json

from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.proposals.validators import (
    ValidatedUpdateMealFoodQuantityOperation,
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


class ProposalValidatorTests(TestCase):
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

        self.other_meal = Meal.objects.create(
            name="Other Meal",
            created_by=self.user,
            is_public=False,
            is_draft=False,
        )

        self.other_mealfood = MealFood.objects.create(
            meal=self.other_meal,
            food=self.food,
            quantity=100,
            order=1,
        )

        self.proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Update quantity",
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

    def test_validate_update_meal_food_quantity_operation(self):
        operations = validate_proposal_operations(
            self.proposal,
        )

        self.assertEqual(len(operations), 1)

        operation = operations[0]

        self.assertIsInstance(
            operation,
            ValidatedUpdateMealFoodQuantityOperation,
        )
        self.assertEqual(operation.type, "update_meal_food_quantity")
        self.assertEqual(operation.mealfood_id, self.mealfood.id)
        self.assertEqual(operation.meal_id, self.meal.id)
        self.assertEqual(operation.food_id, self.food.id)
        self.assertEqual(operation.food_name, "Base Food")
        self.assertEqual(operation.from_quantity, 100.0)
        self.assertEqual(operation.to_quantity, 150.0)

        assert_json_serializable(
            self,
            operation.as_dict(),
        )

    def test_validate_empty_payload_returns_empty_list(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Empty proposal",
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            },
        )

        operations = validate_proposal_operations(
            proposal,
        )

        self.assertEqual(operations, [])

    def test_validate_blocks_unknown_mealfood(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Unknown mealfood",
            proposed_payload={
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": 999999,
                        "from_quantity": 100,
                        "to_quantity": 150,
                    }
                ],
            },
        )

        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_mealfood_not_found",
        ):
            validate_proposal_operations(
                proposal,
            )

    def test_validate_blocks_mealfood_not_in_dailyplan(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="MealFood outside dailyplan",
            proposed_payload={
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": self.other_mealfood.id,
                        "from_quantity": 100,
                        "to_quantity": 150,
                    }
                ],
            },
        )

        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_mealfood_not_in_dailyplan",
        ):
            validate_proposal_operations(
                proposal,
            )

    def test_validate_blocks_from_quantity_mismatch(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Quantity mismatch",
            proposed_payload={
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
            validate_proposal_operations(
                proposal,
            )

    def test_validate_blocks_unchanged_to_quantity(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Unchanged quantity",
            proposed_payload={
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": self.mealfood.id,
                        "from_quantity": 100,
                        "to_quantity": 100,
                    }
                ],
            },
        )

        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_to_quantity_unchanged",
        ):
            validate_proposal_operations(
                proposal,
            )

    def test_validate_reuses_parser_errors(self):
        proposal = NutritionProposal.objects.create(
            dailyplan=self.dailyplan,
            created_by=self.user,
            title="Invalid parser payload",
            proposed_payload={
                "suggested_changes": [
                    {
                        "type": "delete_meal",
                        "meal_id": self.meal.id,
                    }
                ],
            },
        )

        with self.assertRaisesMessage(
            ValueError,
            "unsupported_proposal_operation_type",
        ):
            validate_proposal_operations(
                proposal,
            )