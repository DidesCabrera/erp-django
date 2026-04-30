import json
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.services.commands.proposal_commands import (
    create_validated_dailyplan_proposal,
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


class ProposalValidationIntegrationTests(TestCase):
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

        self.other_dailyplan = DailyPlan.objects.create(
            name="Other Training Day",
            created_by=self.other_user,
            is_public=False,
            is_draft=False,
        )

    def test_create_validated_dailyplan_proposal_stores_validation_summary(self):
        result = create_validated_dailyplan_proposal(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Adjust Training Day",
            summary="Move the plan closer to the requested targets.",
            targets={
                "total_kcal": 200,
                "protein": 30,
                "carbs": 20,
                "fat": 0,
                "ppk": 0.3,
            },
            tolerances={
                "total_kcal": 10,
                "protein": 5,
                "carbs": 5,
                "fat": 1,
                "ppk": 0.05,
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "food_name": "Base Food",
                        "from_quantity": 100,
                        "to_quantity": 150,
                    }
                ],
            },
        )

        proposal = result.proposal

        self.assertEqual(proposal.dailyplan, self.dailyplan)
        self.assertEqual(proposal.created_by, self.user)
        self.assertEqual(proposal.source, NutritionProposal.SOURCE_AI)
        self.assertEqual(
            proposal.status,
            NutritionProposal.STATUS_PENDING_REVIEW,
        )

        self.assertEqual(
            proposal.targets,
            {
                "total_kcal": 200,
                "protein": 30,
                "carbs": 20,
                "fat": 0,
                "ppk": 0.3,
            },
        )

        self.assertEqual(
            proposal.current_snapshot["dailyplan_id"],
            self.dailyplan.id,
        )
        self.assertEqual(
            proposal.current_snapshot["dailyplan_name"],
            "Training Day",
        )
        self.assertEqual(
            proposal.current_snapshot["actual"]["total_kcal"],
            120,
        )
        self.assertEqual(
            proposal.current_snapshot["actual"]["protein"],
            10,
        )
        self.assertEqual(
            proposal.current_snapshot["actual"]["carbs"],
            20,
        )
        self.assertEqual(
            proposal.current_snapshot["actual"]["fat"],
            0,
        )
        self.assertEqual(
            proposal.current_snapshot["actual"]["ppk"],
            0.1,
        )

        self.assertEqual(
            proposal.validation_summary["dailyplan_id"],
            self.dailyplan.id,
        )
        self.assertFalse(
            proposal.validation_summary["within_tolerance"],
        )
        self.assertEqual(
            proposal.validation_summary["delta"]["protein"],
            -20,
        )
        self.assertEqual(
            proposal.validation_summary["delta"]["total_kcal"],
            -80,
        )

        self.assertEqual(
            proposal.proposed_payload["intent"],
            "adjust_dailyplan_to_targets",
        )

        assert_json_serializable(
            self,
            proposal.targets,
        )
        assert_json_serializable(
            self,
            proposal.current_snapshot,
        )
        assert_json_serializable(
            self,
            proposal.proposed_payload,
        )
        assert_json_serializable(
            self,
            proposal.validation_summary,
        )

    def test_create_validated_dailyplan_proposal_uses_default_payload(self):
        result = create_validated_dailyplan_proposal(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Default payload proposal",
            targets={
                "protein": 30,
            },
        )

        proposal = result.proposal

        self.assertEqual(
            proposal.proposed_payload,
            {
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            },
        )

    def test_create_validated_dailyplan_proposal_requires_targets(self):
        with self.assertRaisesMessage(
            ValueError,
            "proposal_targets_required",
        ):
            create_validated_dailyplan_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Missing targets",
                targets={},
            )

    def test_create_validated_dailyplan_proposal_reuses_validation_target_rules(self):
        with self.assertRaisesMessage(
            ValueError,
            "Unsupported target metrics",
        ):
            create_validated_dailyplan_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Invalid target",
                targets={
                    "fiber": 30,
                },
            )

    def test_create_validated_dailyplan_proposal_blocks_other_user_dailyplan(self):
        with self.assertRaises(Exception):
            create_validated_dailyplan_proposal(
                user=self.user,
                dailyplan_id=self.other_dailyplan.id,
                title="Other dailyplan proposal",
                targets={
                    "protein": 30,
                },
            )

    def test_create_validated_dailyplan_proposal_does_not_modify_dailyplan(self):
        result = create_validated_dailyplan_proposal(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Read only validation proposal",
            targets={
                "protein": 30,
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [
                    {
                        "type": "rename_dailyplan",
                        "from_name": "Training Day",
                        "to_name": "Changed Name",
                    }
                ],
            },
        )

        self.dailyplan.refresh_from_db()

        self.assertEqual(
            result.proposal.status,
            NutritionProposal.STATUS_PENDING_REVIEW,
        )
        self.assertEqual(
            self.dailyplan.name,
            "Training Day",
        )