import unittest

from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.tool_handlers import (
    call_proposal_tool,
    create_validated_dailyplan_proposal,
)
from myscoope_mcp.tools import TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL


class FakeMyscoopeAPIClient:
    def __init__(self):
        self.calls = []

    def call_ai_tool_api(self, api_path, payload):
        self.calls.append(
            {
                "api_path": api_path,
                "payload": payload,
            }
        )

        return MCPToolCallResult(
            ok=True,
            data={
                "api_path": api_path,
                "payload": payload,
            },
            error=None,
        )


class MCPProposalToolHandlerTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeMyscoopeAPIClient()

    def test_create_validated_dailyplan_proposal_calls_api_adapter(self):
        result = create_validated_dailyplan_proposal(
            client=self.client,
            dailyplan_id=123,
            title="AI protein proposal",
            summary="Increase protein while keeping calories stable.",
            targets={
                "protein": 190,
                "total_kcal": 2800,
            },
            tolerances={
                "protein": 10,
                "total_kcal": 100,
            },
            proposed_payload={
                "intent": "adjust_dailyplan_to_targets",
                "suggested_changes": [
                    {
                        "type": "update_meal_food_quantity",
                        "mealfood_id": 456,
                        "from_quantity": 100,
                        "to_quantity": 150,
                    }
                ],
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": "/ai-tools/create-validated-dailyplan-proposal/",
                    "payload": {
                        "dailyplan_id": 123,
                        "title": "AI protein proposal",
                        "summary": "Increase protein while keeping calories stable.",
                        "targets": {
                            "protein": 190,
                            "total_kcal": 2800,
                        },
                        "proposed_payload": {
                            "intent": "adjust_dailyplan_to_targets",
                            "suggested_changes": [
                                {
                                    "type": "update_meal_food_quantity",
                                    "mealfood_id": 456,
                                    "from_quantity": 100,
                                    "to_quantity": 150,
                                }
                            ],
                        },
                        "tolerances": {
                            "protein": 10,
                            "total_kcal": 100,
                        },
                    },
                }
            ],
        )

    def test_create_validated_dailyplan_proposal_omits_optional_fields(self):
        result = create_validated_dailyplan_proposal(
            client=self.client,
            dailyplan_id=123,
            title="AI proposal",
            targets={
                "protein": 190,
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": "/ai-tools/create-validated-dailyplan-proposal/",
                    "payload": {
                        "dailyplan_id": 123,
                        "title": "AI proposal",
                        "targets": {
                            "protein": 190,
                        },
                    },
                }
            ],
        )

    def test_call_proposal_tool_dispatches_create_validated_proposal(self):
        result = call_proposal_tool(
            self.client,
            TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
            {
                "dailyplan_id": 123,
                "title": "AI proposal",
                "targets": {
                    "protein": 190,
                },
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls[0]["api_path"],
            "/ai-tools/create-validated-dailyplan-proposal/",
        )

    def test_call_proposal_tool_requires_dailyplan_id(self):
        result = call_proposal_tool(
            self.client,
            TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
            {
                "title": "AI proposal",
                "targets": {
                    "protein": 190,
                },
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "missing_required_argument:dailyplan_id",
        )
        self.assertEqual(
            self.client.calls,
            [],
        )

    def test_call_proposal_tool_requires_title(self):
        result = call_proposal_tool(
            self.client,
            TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
            {
                "dailyplan_id": 123,
                "targets": {
                    "protein": 190,
                },
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "missing_required_argument:title",
        )
        self.assertEqual(
            self.client.calls,
            [],
        )

    def test_call_proposal_tool_requires_targets(self):
        result = call_proposal_tool(
            self.client,
            TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
            {
                "dailyplan_id": 123,
                "title": "AI proposal",
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "missing_required_argument:targets",
        )
        self.assertEqual(
            self.client.calls,
            [],
        )

    def test_call_proposal_tool_rejects_unknown_proposal_tool(self):
        result = call_proposal_tool(
            self.client,
            "unknown_proposal_tool",
            {},
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "unsupported_proposal_tool:unknown_proposal_tool",
        )
        self.assertEqual(
            self.client.calls,
            [],
        )

    def test_no_apply_tool_is_supported_by_proposal_dispatcher(self):
        dangerous_tool_names = [
            "apply_approved_proposal",
            "apply_proposal",
            "apply_validated_proposal",
        ]

        for tool_name in dangerous_tool_names:
            result = call_proposal_tool(
                self.client,
                tool_name,
                {
                    "proposal_id": 999,
                },
            )

            data = result.as_dict()

            self.assertFalse(data["ok"])
            self.assertEqual(
                data["error"]["code"],
                f"unsupported_proposal_tool:{tool_name}",
            )
            self.assertEqual(
                self.client.calls,
                [],
            )


if __name__ == "__main__":
    unittest.main()