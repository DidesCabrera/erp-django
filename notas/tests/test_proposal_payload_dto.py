from django.test import SimpleTestCase

from notas.application.dto.proposal_payloads import (
    CREATE_DAILYPLAN_INTENT,
    CREATE_MEAL_INTENT,
    parse_proposal_payload,
    parse_proposed_dailyplan_payload,
    parse_proposed_meal_payload,
)


class ProposalPayloadDTOTests(SimpleTestCase):
    def test_parse_create_meal_payload(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "Almuerzo alto en proteína",
                "foods": [
                    {
                        "food_id": 10,
                        "quantity": 180,
                        "unit": "g",
                    },
                    {
                        "food_id": 20,
                        "quantity": 120.5,
                    },
                ],
            },
        }

        dto = parse_proposed_meal_payload(payload)

        self.assertEqual(dto.intent, CREATE_MEAL_INTENT)
        self.assertEqual(dto.meal.name, "Almuerzo alto en proteína")
        self.assertEqual(len(dto.meal.foods), 2)

        self.assertEqual(dto.meal.foods[0].food_id, 10)
        self.assertEqual(dto.meal.foods[0].quantity, 180.0)
        self.assertEqual(dto.meal.foods[0].unit, "g")

        self.assertEqual(dto.meal.foods[1].food_id, 20)
        self.assertEqual(dto.meal.foods[1].quantity, 120.5)
        self.assertEqual(dto.meal.foods[1].unit, "g")

        self.assertEqual(
            dto.as_dict(),
            {
                "intent": "create_meal",
                "meal": {
                    "name": "Almuerzo alto en proteína",
                    "foods": [
                        {
                            "food_id": 10,
                            "quantity": 180.0,
                            "unit": "g",
                        },
                        {
                            "food_id": 20,
                            "quantity": 120.5,
                            "unit": "g",
                        },
                    ],
                },
            },
        )

    def test_parse_create_meal_payload_strips_name_and_unit(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "  Desayuno IA  ",
                "foods": [
                    {
                        "food_id": 1,
                        "quantity": 80,
                        "unit": " g ",
                    },
                ],
            },
        }

        dto = parse_proposed_meal_payload(payload)

        self.assertEqual(dto.meal.name, "Desayuno IA")
        self.assertEqual(dto.meal.foods[0].unit, "g")

    def test_parse_create_meal_payload_rejects_invalid_intent(self):
        payload = {
            "intent": "adjust_dailyplan_to_targets",
            "meal": {
                "name": "Meal",
                "foods": [
                    {
                        "food_id": 1,
                        "quantity": 100,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "invalid_proposed_meal_payload_intent",
        ):
            parse_proposed_meal_payload(payload)

    def test_parse_create_meal_payload_requires_meal_name(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "   ",
                "foods": [
                    {
                        "food_id": 1,
                        "quantity": 100,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_meal_name_required",
        ):
            parse_proposed_meal_payload(payload)

    def test_parse_create_meal_payload_requires_foods(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "Meal",
                "foods": [],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_meal_foods_must_not_be_empty",
        ):
            parse_proposed_meal_payload(payload)

    def test_parse_create_meal_payload_requires_food_id(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "Meal",
                "foods": [
                    {
                        "quantity": 100,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_food_item_food_id_required",
        ):
            parse_proposed_meal_payload(payload)

    def test_parse_create_meal_payload_requires_positive_quantity(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "Meal",
                "foods": [
                    {
                        "food_id": 1,
                        "quantity": 0,
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_food_item_quantity_must_be_positive",
        ):
            parse_proposed_meal_payload(payload)

    def test_parse_create_dailyplan_payload(self):
        payload = {
            "intent": CREATE_DAILYPLAN_INTENT,
            "dailyplan": {
                "name": "Día entrenamiento IA",
                "meals": [
                    {
                        "hour": "09:00",
                        "note": "Desayuno",
                        "meal": {
                            "name": "Desayuno alto en energía",
                            "foods": [
                                {
                                    "food_id": 1,
                                    "quantity": 80,
                                    "unit": "g",
                                },
                            ],
                        },
                    },
                    {
                        "hour": None,
                        "note": "",
                        "meal": {
                            "name": "Almuerzo",
                            "foods": [
                                {
                                    "food_id": 2,
                                    "quantity": 200,
                                },
                            ],
                        },
                    },
                ],
            },
        }

        dto = parse_proposed_dailyplan_payload(payload)

        self.assertEqual(dto.intent, CREATE_DAILYPLAN_INTENT)
        self.assertEqual(dto.dailyplan.name, "Día entrenamiento IA")
        self.assertEqual(len(dto.dailyplan.meals), 2)

        self.assertEqual(dto.dailyplan.meals[0].hour, "09:00")
        self.assertEqual(dto.dailyplan.meals[0].note, "Desayuno")
        self.assertEqual(
            dto.dailyplan.meals[0].meal.name,
            "Desayuno alto en energía",
        )
        self.assertEqual(dto.dailyplan.meals[0].meal.foods[0].food_id, 1)
        self.assertEqual(dto.dailyplan.meals[0].meal.foods[0].quantity, 80.0)

        self.assertIsNone(dto.dailyplan.meals[1].hour)
        self.assertEqual(dto.dailyplan.meals[1].note, "")
        self.assertEqual(dto.dailyplan.meals[1].meal.foods[0].unit, "g")

        self.assertEqual(
            dto.as_dict(),
            {
                "intent": "create_dailyplan",
                "dailyplan": {
                    "name": "Día entrenamiento IA",
                    "meals": [
                        {
                            "hour": "09:00",
                            "note": "Desayuno",
                            "meal": {
                                "name": "Desayuno alto en energía",
                                "foods": [
                                    {
                                        "food_id": 1,
                                        "quantity": 80.0,
                                        "unit": "g",
                                    },
                                ],
                            },
                        },
                        {
                            "hour": None,
                            "note": "",
                            "meal": {
                                "name": "Almuerzo",
                                "foods": [
                                    {
                                        "food_id": 2,
                                        "quantity": 200.0,
                                        "unit": "g",
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        )

    def test_parse_create_dailyplan_payload_requires_dailyplan_name(self):
        payload = {
            "intent": CREATE_DAILYPLAN_INTENT,
            "dailyplan": {
                "name": "",
                "meals": [
                    {
                        "meal": {
                            "name": "Meal",
                            "foods": [
                                {
                                    "food_id": 1,
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
            "proposed_dailyplan_name_required",
        ):
            parse_proposed_dailyplan_payload(payload)

    def test_parse_create_dailyplan_payload_requires_meals(self):
        payload = {
            "intent": CREATE_DAILYPLAN_INTENT,
            "dailyplan": {
                "name": "Día entrenamiento IA",
                "meals": [],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_dailyplan_meals_must_not_be_empty",
        ):
            parse_proposed_dailyplan_payload(payload)

    def test_parse_create_dailyplan_payload_requires_nested_meal_foods(self):
        payload = {
            "intent": CREATE_DAILYPLAN_INTENT,
            "dailyplan": {
                "name": "Día entrenamiento IA",
                "meals": [
                    {
                        "hour": "09:00",
                        "note": "Desayuno",
                        "meal": {
                            "name": "Desayuno",
                            "foods": [],
                        },
                    },
                ],
            },
        }

        with self.assertRaisesMessage(
            ValueError,
            "proposed_dailyplan_meal_foods_must_not_be_empty",
        ):
            parse_proposed_dailyplan_payload(payload)

    def test_parse_proposal_payload_dispatches_create_meal(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "Meal",
                "foods": [
                    {
                        "food_id": 1,
                        "quantity": 100,
                    },
                ],
            },
        }

        dto = parse_proposal_payload(payload)

        self.assertEqual(dto.intent, CREATE_MEAL_INTENT)

    def test_parse_proposal_payload_dispatches_create_dailyplan(self):
        payload = {
            "intent": CREATE_DAILYPLAN_INTENT,
            "dailyplan": {
                "name": "DailyPlan",
                "meals": [
                    {
                        "meal": {
                            "name": "Meal",
                            "foods": [
                                {
                                    "food_id": 1,
                                    "quantity": 100,
                                },
                            ],
                        },
                    },
                ],
            },
        }

        dto = parse_proposal_payload(payload)

        self.assertEqual(dto.intent, CREATE_DAILYPLAN_INTENT)

    def test_parse_proposal_payload_rejects_unknown_intent(self):
        payload = {
            "intent": "unknown",
        }

        with self.assertRaisesMessage(
            ValueError,
            "unsupported_proposal_payload_intent",
        ):
            parse_proposal_payload(payload)