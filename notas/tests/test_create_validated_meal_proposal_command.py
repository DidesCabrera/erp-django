from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.services.commands.proposal_commands import (
    create_validated_meal_proposal,
)
from notas.domain.models import DailyPlan, Food, Meal, NutritionProposal


class CreateValidatedMealProposalCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            password="pass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="pass123",
        )

        self.dailyplan = DailyPlan.objects.create(
            name="Día entrenamiento",
            created_by=self.user,
        )

        self.other_dailyplan = DailyPlan.objects.create(
            name="Other DailyPlan",
            created_by=self.other_user,
        )

        self.food = Food.objects.create(
            name="Pechuga pollo",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=self.user,
        )
        
        self.private_other_food = Food.objects.create(
            name="Private Other Food",
            protein=100,
            carbs=100,
            fat=100,
            created_by=self.other_user,
        )

    def test_create_validated_meal_proposal_creates_pending_review_proposal(self):
        payload = {
            "intent": "create_meal",
            "meal": {
                "name": "Almuerzo IA",
                "foods": [
                    {
                        "food_id": self.food.id,
                        "quantity": 200,
                        "unit": "g",
                    },
                ],
            },
        }

        result = create_validated_meal_proposal(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Propuesta MCP - Almuerzo IA",
            summary="Comida propuesta desde MCP.",
            source=NutritionProposal.SOURCE_MCP,
            targets={
                "protein": 60,
                "total_kcal": 500,
            },
            proposed_payload=payload,
        )

        proposal = result.proposal

        self.assertEqual(proposal.dailyplan_id, self.dailyplan.id)
        self.assertEqual(proposal.created_by_id, self.user.id)
        self.assertEqual(proposal.status, NutritionProposal.STATUS_PENDING_REVIEW)
        self.assertEqual(proposal.source, NutritionProposal.SOURCE_MCP)
        self.assertEqual(proposal.title, "Propuesta MCP - Almuerzo IA")
        self.assertEqual(proposal.summary, "Comida propuesta desde MCP.")
        self.assertEqual(
            proposal.targets,
            {
                "protein": 60,
                "total_kcal": 500,
            },
        )
        self.assertEqual(
            proposal.proposed_payload,
            {
                "intent": "create_meal",
                "meal": {
                    "name": "Almuerzo IA",
                    "foods": [
                        {
                            "food_id": self.food.id,
                            "quantity": 200.0,
                            "unit": "g",
                        },
                    ],
                },
            },
        )

        self.assertEqual(
            proposal.validation_summary["payload_validation"],
            {
                "is_valid": True,
                "intent": "create_meal",
            },
        )

        simulation = proposal.validation_summary["simulation"]

        self.assertEqual(simulation["intent"], "create_meal")
        self.assertIsNone(simulation["dailyplan"])
        self.assertEqual(simulation["meal"]["name"], "Almuerzo IA")
        self.assertEqual(len(simulation["meal"]["foods"]), 1)
        self.assertEqual(
            simulation["meal"]["foods"][0]["food_name"],
            "Pechuga pollo",
        )
        self.assertAlmostEqual(
            simulation["meal"]["kpis"]["protein"],
            62.0,
        )
        self.assertAlmostEqual(
            simulation["meal"]["kpis"]["fat"],
            7.2,
        )
        self.assertAlmostEqual(
            simulation["meal"]["kpis"]["total_kcal"],
            312.8,
        )
        self.assertEqual(
            proposal.current_snapshot,
            {
                "dailyplan_id": self.dailyplan.id,
                "context": "meal_proposal",
            },
        )

    def test_create_validated_meal_proposal_does_not_create_meal(self):
        payload = {
            "intent": "create_meal",
            "meal": {
                "name": "Almuerzo IA",
                "foods": [
                    {
                        "food_id": self.food.id,
                        "quantity": 200,
                    },
                ],
            },
        }

        create_validated_meal_proposal(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Propuesta MCP - Almuerzo IA",
            proposed_payload=payload,
        )

        self.assertEqual(Meal.objects.count(), 0)

    def test_create_validated_meal_proposal_rejects_non_meal_payload(self):
        payload = {
            "intent": "create_dailyplan",
            "dailyplan": {
                "name": "Día IA",
                "meals": [
                    {
                        "meal": {
                            "name": "Meal",
                            "foods": [
                                {
                                    "food_id": self.food.id,
                                    "quantity": 100,
                                },
                            ],
                        },
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposal_payload_must_be_create_meal",
        ):
            create_validated_meal_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )

    def test_create_validated_meal_proposal_rejects_invalid_payload(self):
        payload = {
            "intent": "create_meal",
            "meal": {
                "name": "Invalid",
                "foods": [
                    {
                        "food_id": self.food.id,
                        "quantity": 0,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_food_item_quantity_must_be_positive",
        ):
            create_validated_meal_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )

    def test_create_validated_meal_proposal_rejects_unowned_dailyplan(self):
        payload = {
            "intent": "create_meal",
            "meal": {
                "name": "Meal",
                "foods": [
                    {
                        "food_id": self.food.id,
                        "quantity": 100,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "dailyplan_not_available_for_proposal",
        ):
            create_validated_meal_proposal(
                user=self.user,
                dailyplan_id=self.other_dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )
            
    def test_create_validated_meal_proposal_rejects_unreadable_food(self):
        payload = {
            "intent": "create_meal",
            "meal": {
                "name": "Invalid Meal",
                "foods": [
                    {
                        "food_id": self.private_other_food.id,
                        "quantity": 100,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(Exception, "No Food matches the given query."):
            create_validated_meal_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )