from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from notas.application.ai_tools.proposal_tools import (
    create_validated_meal_proposal_tool,
)
from notas.domain.models import DailyPlan, Food


class AIMealProposalToolTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            password="pass123",
        )

        self.dailyplan = DailyPlan.objects.create(
            name="Día entrenamiento",
            created_by=self.user,
        )

        self.food = Food.objects.create(
            name="Pechuga pollo",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=self.user,
        )

    def test_create_validated_meal_proposal_tool_returns_proposal(self):
        result = create_validated_meal_proposal_tool(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Propuesta MCP - Almuerzo IA",
            summary="Comida propuesta desde MCP.",
            targets={
                "protein": 60,
            },
            proposed_payload={
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
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertIsNone(data["error"])

        proposal = data["data"]["proposal"]

        self.assertEqual(proposal["dailyplan_id"], self.dailyplan.id)
        self.assertEqual(proposal["status"], "pending_review")
        self.assertEqual(proposal["title"], "Propuesta MCP - Almuerzo IA")
        self.assertEqual(proposal["targets"], {"protein": 60})
        self.assertEqual(proposal["proposed_payload"]["intent"], "create_meal")
        self.assertEqual(
            proposal["validation_summary"]["payload_validation"],
            {
                "is_valid": True,
                "intent": "create_meal",
            },
        )

    def test_create_validated_meal_proposal_tool_returns_error_for_invalid_payload(self):
        result = create_validated_meal_proposal_tool(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Invalid",
            proposed_payload={
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
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(data["data"], {})
        self.assertIsNotNone(data["error"])

    def test_create_validated_meal_proposal_tool_requires_authenticated_user(self):
        result = create_validated_meal_proposal_tool(
            user=AnonymousUser(),
            dailyplan_id=self.dailyplan.id,
            title="Invalid",
            proposed_payload={
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
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(data["data"], {})
        self.assertIsNotNone(data["error"])