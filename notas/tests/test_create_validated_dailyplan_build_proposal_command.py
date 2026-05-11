from django.contrib.auth.models import User
from django.test import TestCase

from notas.application.services.commands.proposal_commands import (
    create_validated_dailyplan_build_proposal,
)
from notas.domain.models import DailyPlan, Food, Meal, NutritionProposal


class CreateValidatedDailyPlanBuildProposalCommandTests(TestCase):
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
            name="Día contexto",
            created_by=self.user,
        )

        self.other_dailyplan = DailyPlan.objects.create(
            name="Other DailyPlan",
            created_by=self.other_user,
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

        self.private_other_food = Food.objects.create(
            name="Private Other Food",
            protein=100,
            carbs=100,
            fat=100,
            created_by=self.other_user,
        )

    def test_create_validated_dailyplan_build_proposal_creates_pending_review_proposal(self):
        payload = {
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
                                    "unit": "g",
                                },
                            ],
                        },
                    },
                ],
            },
        }

        result = create_validated_dailyplan_build_proposal(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Propuesta MCP - Día entrenamiento IA",
            summary="DailyPlan propuesto desde MCP.",
            source=NutritionProposal.SOURCE_MCP,
            targets={
                "protein": 190,
                "total_kcal": 2800,
            },
            proposed_payload=payload,
        )

        proposal = result.proposal

        self.assertEqual(proposal.dailyplan_id, self.dailyplan.id)
        self.assertEqual(proposal.created_by_id, self.user.id)
        self.assertEqual(proposal.status, NutritionProposal.STATUS_PENDING_REVIEW)
        self.assertEqual(proposal.source, NutritionProposal.SOURCE_MCP)
        self.assertEqual(proposal.title, "Propuesta MCP - Día entrenamiento IA")
        self.assertEqual(proposal.summary, "DailyPlan propuesto desde MCP.")
        self.assertEqual(
            proposal.targets,
            {
                "protein": 190,
                "total_kcal": 2800,
            },
        )
        self.assertEqual(
            proposal.current_snapshot,
            {
                "dailyplan_id": self.dailyplan.id,
                "context": "dailyplan_build_proposal",
            },
        )

        self.assertEqual(proposal.proposed_payload["intent"], "create_dailyplan")
        self.assertEqual(
            proposal.proposed_payload["dailyplan"]["name"],
            "Día entrenamiento IA",
        )
        self.assertEqual(len(proposal.proposed_payload["dailyplan"]["meals"]), 2)

        self.assertEqual(
            proposal.validation_summary["payload_validation"],
            {
                "is_valid": True,
                "intent": "create_dailyplan",
            },
        )

        simulation = proposal.validation_summary["simulation"]

        self.assertEqual(simulation["intent"], "create_dailyplan")
        self.assertIsNone(simulation["meal"])

        simulated_dailyplan = simulation["dailyplan"]

        self.assertEqual(
            simulated_dailyplan["name"],
            "Día entrenamiento IA",
        )
        self.assertEqual(len(simulated_dailyplan["meals"]), 2)

        self.assertAlmostEqual(
            simulated_dailyplan["kpis"]["protein"],
            64.7,
        )
        self.assertAlmostEqual(
            simulated_dailyplan["kpis"]["carbs"],
            28.0,
        )
        self.assertAlmostEqual(
            simulated_dailyplan["kpis"]["fat"],
            7.5,
        )
        self.assertAlmostEqual(
            simulated_dailyplan["kpis"]["total_kcal"],
            438.3,
        )

    def test_create_validated_dailyplan_build_proposal_does_not_create_meal(self):
        payload = {
            "intent": "create_dailyplan",
            "dailyplan": {
                "name": "Día entrenamiento IA",
                "meals": [
                    {
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
        }

        create_validated_dailyplan_build_proposal(
            user=self.user,
            dailyplan_id=self.dailyplan.id,
            title="Propuesta MCP - Día IA",
            proposed_payload=payload,
        )

        self.assertEqual(Meal.objects.count(), 0)
        self.assertEqual(DailyPlan.objects.count(), 2)

    def test_create_validated_dailyplan_build_proposal_rejects_non_dailyplan_payload(self):
        payload = {
            "intent": "create_meal",
            "meal": {
                "name": "Almuerzo IA",
                "foods": [
                    {
                        "food_id": self.chicken.id,
                        "quantity": 200,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposal_payload_must_be_create_dailyplan",
        ):
            create_validated_dailyplan_build_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )

    def test_create_validated_dailyplan_build_proposal_rejects_invalid_payload(self):
        payload = {
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
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_dailyplan_meal_hour_out_of_range",
        ):
            create_validated_dailyplan_build_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )

    def test_create_validated_dailyplan_build_proposal_rejects_unreadable_food(self):
        payload = {
            "intent": "create_dailyplan",
            "dailyplan": {
                "name": "Invalid",
                "meals": [
                    {
                        "meal": {
                            "name": "Invalid Meal",
                            "foods": [
                                {
                                    "food_id": self.private_other_food.id,
                                    "quantity": 100,
                                },
                            ],
                        },
                    },
                ],
            },
        }

        with self.assertRaisesMessage(Exception, "No Food matches the given query."):
            create_validated_dailyplan_build_proposal(
                user=self.user,
                dailyplan_id=self.dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )

    def test_create_validated_dailyplan_build_proposal_rejects_unowned_context_dailyplan(self):
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
                                    "food_id": self.chicken.id,
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
            "dailyplan_not_available_for_proposal",
        ):
            create_validated_dailyplan_build_proposal(
                user=self.user,
                dailyplan_id=self.other_dailyplan.id,
                title="Invalid",
                proposed_payload=payload,
            )