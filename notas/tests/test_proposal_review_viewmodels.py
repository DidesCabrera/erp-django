from django.test import SimpleTestCase

from notas.presentation.proposals.proposal_review_viewmodels import (
    build_proposal_review_vm,
)


class ProposalReviewViewModelTests(SimpleTestCase):
    def test_build_review_vm_for_create_meal_proposal(self):
        proposal = {
            "id": 10,
            "title": "Propuesta comida IA",
            "summary": "Comida propuesta.",
            "dailyplan_id": 128,
            "dailyplan_name": "Menú Dia Entrenamiento",
            "created_by_username": "felipe",
            "reviewed_by_username": None,
            "status": "pending_review",
            "is_reviewable": True,
            "is_final": False,
            "targets": {
                "protein": 60,
            },
            "proposed_payload": {
                "intent": "create_meal",
                "meal": {
                    "name": "Almuerzo IA",
                    "foods": [
                        {
                            "food_id": 1,
                            "quantity": 200,
                            "unit": "g",
                        },
                    ],
                },
            },
            "validation_summary": {
                "payload_validation": {
                    "is_valid": True,
                    "intent": "create_meal",
                },
                "simulation": {
                    "intent": "create_meal",
                    "meal": {
                        "name": "Almuerzo IA",
                        "kpis": {
                            "protein": 62,
                            "total_kcal": 312.8,
                        },
                    },
                    "dailyplan": None,
                },
            },
        }

        vm = build_proposal_review_vm(proposal)

        self.assertEqual(vm.proposal_id, 10)
        self.assertEqual(vm.title, "Propuesta comida IA")
        self.assertEqual(vm.dailyplan_id, 128)
        self.assertEqual(vm.dailyplan_name, "Menú Dia Entrenamiento")
        self.assertEqual(vm.status.status, "pending_review")
        self.assertTrue(vm.status.is_reviewable)
        self.assertFalse(vm.status.is_final)

        self.assertEqual(vm.payload.intent, "create_meal")
        self.assertTrue(vm.payload.is_create_meal)
        self.assertFalse(vm.payload.is_create_dailyplan)
        self.assertEqual(vm.payload.targets, {"protein": 60})
        self.assertEqual(
            vm.payload.simulation["meal"]["kpis"]["protein"],
            62,
        )

    def test_build_review_vm_for_create_dailyplan_proposal(self):
        proposal = {
            "id": 20,
            "title": "Propuesta DailyPlan IA",
            "summary": "",
            "dailyplan_id": 128,
            "dailyplan_name": "Menú Dia Entrenamiento",
            "created_by_username": "felipe",
            "reviewed_by_username": None,
            "status": "pending_review",
            "is_reviewable": True,
            "is_final": False,
            "targets": {
                "protein": 190,
                "total_kcal": 2800,
            },
            "proposed_payload": {
                "intent": "create_dailyplan",
                "dailyplan": {
                    "name": "Día IA",
                    "meals": [],
                },
            },
            "validation_summary": {
                "payload_validation": {
                    "is_valid": True,
                    "intent": "create_dailyplan",
                },
                "simulation": {
                    "intent": "create_dailyplan",
                    "meal": None,
                    "dailyplan": {
                        "name": "Día IA",
                        "kpis": {
                            "protein": 2,
                            "total_kcal": 34,
                        },
                    },
                },
            },
        }

        vm = build_proposal_review_vm(proposal)

        self.assertEqual(vm.payload.intent, "create_dailyplan")
        self.assertFalse(vm.payload.is_create_meal)
        self.assertTrue(vm.payload.is_create_dailyplan)
        self.assertEqual(
            vm.payload.simulation["dailyplan"]["kpis"]["total_kcal"],
            34,
        )

    def test_build_review_vm_handles_missing_optional_payload_fields(self):
        proposal = {
            "id": 30,
            "title": "Legacy proposal",
            "status": "pending_review",
            "is_reviewable": True,
            "is_final": False,
        }

        vm = build_proposal_review_vm(proposal)

        self.assertEqual(vm.proposal_id, 30)
        self.assertEqual(vm.title, "Legacy proposal")
        self.assertIsNone(vm.payload.intent)
        self.assertFalse(vm.payload.is_create_meal)
        self.assertFalse(vm.payload.is_create_dailyplan)
        self.assertEqual(vm.payload.proposed_payload, {})
        self.assertIsNone(vm.payload.simulation)
        self.assertEqual(vm.payload.targets, {})

    def test_review_vm_as_dict_is_template_friendly(self):
        proposal = {
            "id": 40,
            "title": "Propuesta comida IA",
            "summary": "",
            "dailyplan_id": 128,
            "dailyplan_name": "Menú Dia Entrenamiento",
            "created_by_username": "felipe",
            "reviewed_by_username": None,
            "status": "pending_review",
            "is_reviewable": True,
            "is_final": False,
            "targets": {},
            "proposed_payload": {
                "intent": "create_meal",
            },
            "validation_summary": {
                "simulation": {
                    "intent": "create_meal",
                },
            },
        }

        data = build_proposal_review_vm(proposal).as_dict()

        self.assertEqual(
            data,
            {
                "proposal_id": 40,
                "title": "Propuesta comida IA",
                "summary": "",
                "dailyplan_id": 128,
                "dailyplan_name": "Menú Dia Entrenamiento",
                "created_by_username": "felipe",
                "reviewed_by_username": None,
                "status": {
                    "status": "pending_review",
                    "is_reviewable": True,
                    "is_final": False,
                },
                "payload": {
                    "intent": "create_meal",
                    "is_create_meal": True,
                    "is_create_dailyplan": False,
                    "proposed_payload": {
                        "intent": "create_meal",
                    },
                    "simulation": {
                        "intent": "create_meal",
                    },
                    "targets": {},
                },
            },
        )