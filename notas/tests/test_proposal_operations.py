import json

from django.test import SimpleTestCase

from notas.application.proposals.operations import (
    OPERATION_UPDATE_MEAL_FOOD_QUANTITY,
    UpdateMealFoodQuantityOperation,
    parse_proposal_operations,
)


def assert_json_serializable(test_case, value):
    try:
        json.dumps(value)
    except TypeError as exc:
        test_case.fail(f"Value is not JSON serializable: {exc}")


class ProposalOperationTests(SimpleTestCase):
    def test_parse_update_meal_food_quantity_operation(self):
        operations = parse_proposal_operations(
            {
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": 123,
                        "from_quantity": 100,
                        "to_quantity": 150,
                    }
                ],
            }
        )

        self.assertEqual(len(operations), 1)

        operation = operations[0]

        self.assertIsInstance(
            operation,
            UpdateMealFoodQuantityOperation,
        )
        self.assertEqual(
            operation.type,
            OPERATION_UPDATE_MEAL_FOOD_QUANTITY,
        )
        self.assertEqual(operation.mealfood_id, 123)
        self.assertEqual(operation.from_quantity, 100.0)
        self.assertEqual(operation.to_quantity, 150.0)

        assert_json_serializable(
            self,
            operation.as_dict(),
        )

    def test_parse_empty_suggested_changes_returns_empty_list(self):
        operations = parse_proposal_operations(
            {
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [],
            }
        )

        self.assertEqual(operations, [])

    def test_parse_missing_suggested_changes_defaults_to_empty_list(self):
        operations = parse_proposal_operations(
            {
                "intent": "adjust_dailyplan_to_targets",
            }
        )

        self.assertEqual(operations, [])

    def test_parse_rejects_non_object_payload(self):
        with self.assertRaisesMessage(
            ValueError,
            "proposal_payload_must_be_object",
        ):
            parse_proposal_operations(None)

    def test_parse_rejects_non_list_suggested_changes(self):
        with self.assertRaisesMessage(
            ValueError,
            "proposal_suggested_changes_must_be_list",
        ):
            parse_proposal_operations(
                {
                    "suggested_changes": {
                        "type": "update_meal_food_quantity",
                    },
                }
            )

    def test_parse_rejects_non_object_operation(self):
        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_must_be_object",
        ):
            parse_proposal_operations(
                {
                    "suggested_changes": [
                        "update_meal_food_quantity",
                    ],
                }
            )

    def test_parse_rejects_unsupported_operation_type(self):
        with self.assertRaisesMessage(
            ValueError,
            "unsupported_proposal_operation_type",
        ):
            parse_proposal_operations(
                {
                    "suggested_changes": [
                        {
                            "type": "delete_meal",
                            "meal_id": 10,
                        }
                    ],
                }
            )

    def test_parse_rejects_missing_required_keys(self):
        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_missing_keys:mealfood_id",
        ):
            parse_proposal_operations(
                {
                    "suggested_changes": [
                        {
                            "type": "update_meal_food_quantity",
                            "from_quantity": 100,
                            "to_quantity": 150,
                        }
                    ],
                }
            )

    def test_parse_rejects_invalid_mealfood_id(self):
        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_invalid_mealfood_id",
        ):
            parse_proposal_operations(
                {
                    "suggested_changes": [
                        {
                            "type": "update_meal_food_quantity",
                            "mealfood_id": 0,
                            "from_quantity": 100,
                            "to_quantity": 150,
                        }
                    ],
                }
            )

    def test_parse_rejects_invalid_quantities(self):
        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_invalid_from_quantity",
        ):
            parse_proposal_operations(
                {
                    "suggested_changes": [
                        {
                            "type": "update_meal_food_quantity",
                            "mealfood_id": 123,
                            "from_quantity": -1,
                            "to_quantity": 150,
                        }
                    ],
                }
            )

        with self.assertRaisesMessage(
            ValueError,
            "proposal_operation_invalid_to_quantity",
        ):
            parse_proposal_operations(
                {
                    "suggested_changes": [
                        {
                            "type": "update_meal_food_quantity",
                            "mealfood_id": 123,
                            "from_quantity": 100,
                            "to_quantity": 0,
                        }
                    ],
                }
            )