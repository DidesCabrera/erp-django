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
                    "meal": None,
                    "dailyplan": None,
                },
            },
        )
    
    def test_build_review_vm_includes_create_meal_render_data(self):
        proposal = {
            "id": 50,
            "title": "Comida AI",
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
                "total_kcal": 500,
            },
            "proposed_payload": {
                "intent": "create_meal",
                "meal": {
                    "name": "Almuerzo IA",
                    "foods": [],
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
                        "foods": [
                            {
                                "food_id": 10,
                                "food_name": "Pechuga pollo",
                                "quantity": 200,
                                "unit": "g",
                                "protein": 62,
                                "carbs": 0,
                                "fat": 7.2,
                                "total_kcal": 312.8,
                            },
                        ],
                        "kpis": {
                            "total_kcal": 312.8,
                            "protein": 62,
                            "carbs": 0,
                            "fat": 7.2,
                            "ppk": 0.62,
                            "alloc_protein": 79.28,
                            "alloc_carbs": 0,
                            "alloc_fat": 20.72,
                        },
                    },
                    "dailyplan": None,
                },
            },
        }

        vm = build_proposal_review_vm(proposal)

        self.assertIsNotNone(vm.payload.meal)
        self.assertEqual(vm.payload.meal.name, "Almuerzo IA")
        self.assertEqual(len(vm.payload.meal.foods), 1)

        food = vm.payload.meal.foods[0]

        self.assertEqual(food.food_id, 10)
        self.assertEqual(food.food_name, "Pechuga pollo")
        self.assertEqual(food.quantity, 200.0)
        self.assertEqual(food.unit, "g")
        self.assertEqual(food.protein, 62.0)
        self.assertEqual(food.total_kcal, 312.8)

        self.assertIsNotNone(vm.payload.meal.kpis)
        self.assertEqual(vm.payload.meal.kpis.protein, 62.0)
        self.assertEqual(vm.payload.meal.kpis.total_kcal, 312.8)
        self.assertEqual(vm.payload.meal.kpis.ppk, 0.62)


    def test_build_review_vm_includes_create_dailyplan_render_data(self):
        proposal = {
            "id": 60,
            "title": "Plan AI",
            "summary": "DailyPlan propuesto.",
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
                    "name": "Día entrenamiento IA",
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
                        "name": "Día entrenamiento IA",
                        "meals": [
                            {
                                "hour": "09:00",
                                "note": "Desayuno",
                                "meal": {
                                    "name": "Desayuno IA",
                                    "foods": [
                                        {
                                            "food_id": 128,
                                            "food_name": "a nuevo egg TEST",
                                            "quantity": 200,
                                            "unit": "g",
                                            "protein": 2,
                                            "carbs": 2,
                                            "fat": 2,
                                            "total_kcal": 34,
                                        },
                                    ],
                                    "kpis": {
                                        "total_kcal": 34,
                                        "protein": 2,
                                        "carbs": 2,
                                        "fat": 2,
                                        "ppk": 0.02,
                                        "alloc_protein": 23.52,
                                        "alloc_carbs": 23.52,
                                        "alloc_fat": 52.94,
                                    },
                                },
                            },
                        ],
                        "kpis": {
                            "total_kcal": 34,
                            "protein": 2,
                            "carbs": 2,
                            "fat": 2,
                            "ppk": 0.02,
                            "alloc_protein": 23.52,
                            "alloc_carbs": 23.52,
                            "alloc_fat": 52.94,
                        },
                    },
                },
            },
        }

        vm = build_proposal_review_vm(proposal)

        self.assertIsNone(vm.payload.meal)
        self.assertIsNotNone(vm.payload.dailyplan)

        dailyplan = vm.payload.dailyplan

        self.assertEqual(dailyplan.name, "Día entrenamiento IA")
        self.assertEqual(len(dailyplan.meals), 1)
        self.assertIsNotNone(dailyplan.kpis)
        self.assertEqual(dailyplan.kpis.total_kcal, 34.0)
        self.assertEqual(dailyplan.kpis.protein, 2.0)

        dailyplan_meal = dailyplan.meals[0]

        self.assertEqual(dailyplan_meal.hour, "09:00")
        self.assertEqual(dailyplan_meal.note, "Desayuno")
        self.assertEqual(dailyplan_meal.meal.name, "Desayuno IA")
        self.assertEqual(len(dailyplan_meal.meal.foods), 1)

        food = dailyplan_meal.meal.foods[0]

        self.assertEqual(food.food_id, 128)
        self.assertEqual(food.food_name, "a nuevo egg TEST")
        self.assertEqual(food.quantity, 200.0)
        self.assertEqual(food.total_kcal, 34.0)

