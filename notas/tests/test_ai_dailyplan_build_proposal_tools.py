from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from notas.application.ai_tools.proposal_tools import (
    create_validated_dailyplan_build_proposal_tool,
)
from notas.domain.models import DailyPlan, Food


class AIDailyPlanBuildProposalToolTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="felipe",
            password="pass123",
        )

        self.dailyplan = DailyPlan.objects.create(
            name="Día contexto",
            created_by=self.user,
        )

        self.chicken = Food.objects.create(
            name="Pechuga pollo",
            protein=31,
            carbs=0,
            fat=3.6,
            created_by=self.user,
        )

        self.rice = Food.objects.create(
            name="Arroz blanco",
            protein=2.7,
            carbs=28,
            fat=0.3,
            created_by=self.user,
        )

    def test_create_validated_dailyplan_build_proposal_tool_returns_proposal(self):
        result = create_validated_dailyplan_build_proposal_tool(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Propuesta MCP - Día entrenamiento IA",
            summary="DailyPlan propuesto desde AI Tool.",
            targets={
                "protein": 190,
                "total_kcal": 2800,
            },
            proposed_payload={
                "intent": "create_dailyplan",
                "dailyplan": {
                    "name": "Día entrenamiento IA",
                    "meals": [
                        {
                            "hour": "09:00",
                            "note": "Desayuno",
                            "meal": {
                                "name": "Desayuno IA",
                                "foods": [
                                    {
                                        "food_id": self.rice.id,
                                        "quantity": 100,
                                    },
                                ],
                            },
                        },
                        {
                            "hour": "14:30",
                            "note": "Almuerzo",
                            "meal": {
                                "name": "Almuerzo IA",
                                "foods": [
                                    {
                                        "food_id": self.chicken.id,
                                        "quantity": 200,
                                    },
                                ],
                            },
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
        self.assertEqual(proposal["title"], "Propuesta MCP - Día entrenamiento IA")
        self.assertEqual(
            proposal["targets"],
            {
                "protein": 190,
                "total_kcal": 2800,
            },
        )
        self.assertEqual(
            proposal["proposed_payload"]["intent"],
            "create_dailyplan",
        )
        self.assertEqual(
            proposal["validation_summary"]["payload_validation"],
            {
                "is_valid": True,
                "intent": "create_dailyplan",
            },
        )

        simulation = proposal["validation_summary"]["simulation"]

        self.assertEqual(simulation["intent"], "create_dailyplan")
        self.assertIsNone(simulation["meal"])
        self.assertEqual(
            simulation["dailyplan"]["name"],
            "Día entrenamiento IA",
        )
        self.assertAlmostEqual(
            simulation["dailyplan"]["kpis"]["protein"],
            64.7,
        )
        self.assertAlmostEqual(
            simulation["dailyplan"]["kpis"]["total_kcal"],
            438.3,
        )

    def test_create_validated_dailyplan_build_proposal_tool_returns_error_for_invalid_payload(self):
        result = create_validated_dailyplan_build_proposal_tool(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Invalid",
            proposed_payload={
                "intent": "create_dailyplan",
                "dailyplan": {
                    "name": "Invalid",
                    "meals": [
                        {
                            "hour": "25:00",
                            "meal": {
                                "name": "Meal",
                                "foods": [
                                    {
                                        "food_id": self.chicken.id,
                                        "quantity": 100,
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(data["data"], {})
        self.assertIsNotNone(data["error"])

    def test_create_validated_dailyplan_build_proposal_tool_requires_authenticated_user(self):
        result = create_validated_dailyplan_build_proposal_tool(
            user=AnonymousUser(),
            dailyplan_id=self.dailyplan.id,
            title="Invalid",
            proposed_payload={
                "intent": "create_dailyplan",
                "dailyplan": {
                    "name": "Día IA",
                    "meals": [
                        {
                            "meal": {
                                "name": "Meal",
                                "foods": [
                                    {
                                        "food_id": self.chicken.id,
                                        "quantity": 100,
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(data["data"], {})
        self.assertIsNotNone(data["error"])