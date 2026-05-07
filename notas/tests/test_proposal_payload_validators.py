from django.test import SimpleTestCase

from notas.application.dto.proposal_payloads import (
    CREATE_DAILYPLAN_INTENT,
    CREATE_MEAL_INTENT,
)
from notas.application.validation.proposal_payload_validators import (
    is_create_dailyplan_payload,
    is_create_meal_payload,
    validate_proposal_payload,
    validate_proposal_payload_or_raise,
)


class ProposalPayloadValidatorTests(SimpleTestCase):
    def test_validate_create_meal_payload_returns_valid_result(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "Almuerzo alto en proteína",
                "foods": [
                    {
                        "food_id": 1,
                        "quantity": 180,
                        "unit": "g",
                    },
                ],
            },
        }

        result = validate_proposal_payload(payload)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.intent, CREATE_MEAL_INTENT)
        self.assertEqual(result.errors, [])
        self.assertIsNotNone(result.parsed_payload)
        self.assertEqual(
            result.parsed_payload.as_dict(),
            {
                "intent": "create_meal",
                "meal": {
                    "name": "Almuerzo alto en proteína",
                    "foods": [
                        {
                            "food_id": 1,
                            "quantity": 180.0,
                            "unit": "g",
                        },
                    ],
                },
            },
        )

    def test_validate_create_dailyplan_payload_returns_valid_result(self):
        payload = {
            "intent": CREATE_DAILYPLAN_INTENT,
            "dailyplan": {
                "name": "Día entrenamiento IA",
                "meals": [
                    {
                        "hour": "9:05",
                        "note": "Desayuno",
                        "meal": {
                            "name": "Desayuno",
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

        result = validate_proposal_payload(payload)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.intent, CREATE_DAILYPLAN_INTENT)
        self.assertEqual(result.errors, [])
        self.assertIsNotNone(result.parsed_payload)
        self.assertEqual(
            result.parsed_payload.as_dict(),
            {
                "intent": "create_dailyplan",
                "dailyplan": {
                    "name": "Día entrenamiento IA",
                    "meals": [
                        {
                            "hour": "09:05",
                            "note": "Desayuno",
                            "meal": {
                                "name": "Desayuno",
                                "foods": [
                                    {
                                        "food_id": 1,
                                        "quantity": 100.0,
                                        "unit": "g",
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        )

    def test_validate_payload_returns_error_for_unknown_intent(self):
        payload = {
            "intent": "unknown",
        }

        result = validate_proposal_payload(payload)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.intent, "unknown")
        self.assertIsNone(result.parsed_payload)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(
            result.errors[0].as_dict(),
            {
                "code": "unsupported_proposal_payload_intent",
                "message": "Proposal payload intent is not supported.",
                "field": "intent",
            },
        )

    def test_validate_payload_returns_error_for_missing_meal_name(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "",
                "foods": [
                    {
                        "food_id": 1,
                        "quantity": 100,
                    },
                ],
            },
        }

        result = validate_proposal_payload(payload)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.intent, CREATE_MEAL_INTENT)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].code, "proposed_meal_name_required")
        self.assertEqual(result.errors[0].field, "meal.name")

    def test_validate_payload_returns_error_for_invalid_dailyplan_hour(self):
        payload = {
            "intent": CREATE_DAILYPLAN_INTENT,
            "dailyplan": {
                "name": "Día entrenamiento IA",
                "meals": [
                    {
                        "hour": "25:00",
                        "note": "Desayuno",
                        "meal": {
                            "name": "Desayuno",
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

        result = validate_proposal_payload(payload)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.intent, CREATE_DAILYPLAN_INTENT)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(
            result.errors[0].code,
            "proposed_dailyplan_meal_hour_out_of_range",
        )
        self.assertEqual(result.errors[0].field, "dailyplan.meals[].hour")

    def test_validate_payload_or_raise_returns_parsed_payload_when_valid(self):
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

        parsed_payload = validate_proposal_payload_or_raise(payload)

        self.assertEqual(parsed_payload.intent, CREATE_MEAL_INTENT)

    def test_validate_payload_or_raise_raises_error_code_when_invalid(self):
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
            validate_proposal_payload_or_raise(payload)

    def test_is_create_meal_payload(self):
        self.assertTrue(
            is_create_meal_payload(
                {
                    "intent": CREATE_MEAL_INTENT,
                }
            )
        )
        self.assertFalse(
            is_create_meal_payload(
                {
                    "intent": CREATE_DAILYPLAN_INTENT,
                }
            )
        )

    def test_is_create_dailyplan_payload(self):
        self.assertTrue(
            is_create_dailyplan_payload(
                {
                    "intent": CREATE_DAILYPLAN_INTENT,
                }
            )
        )
        self.assertFalse(
            is_create_dailyplan_payload(
                {
                    "intent": CREATE_MEAL_INTENT,
                }
            )
        )

    def test_validation_result_as_dict_for_invalid_payload(self):
        payload = {
            "intent": CREATE_MEAL_INTENT,
            "meal": {
                "name": "",
                "foods": [],
            },
        }

        result = validate_proposal_payload(payload)

        self.assertEqual(
            result.as_dict(),
            {
                "is_valid": False,
                "intent": CREATE_MEAL_INTENT,
                "errors": [
                    {
                        "code": "proposed_meal_name_required",
                        "message": "Meal proposal requires a non-empty meal name.",
                        "field": "meal.name",
                    },
                ],
                "parsed_payload": None,
            },
        )