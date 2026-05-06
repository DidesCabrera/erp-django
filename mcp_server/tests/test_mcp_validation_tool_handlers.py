import unittest

from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.tool_handlers import (
    call_validation_tool,
    compare_dailyplan_to_targets,
)
from myscoope_mcp.tools import TOOL_COMPARE_DAILYPLAN_TO_TARGETS


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


class MCPValidationToolHandlerTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeMyscoopeAPIClient()

    def test_compare_dailyplan_to_targets_calls_api_adapter(self):
        result = compare_dailyplan_to_targets(
            client=self.client,
            dailyplan_id=123,
            targets={
                "protein": 190,
                "total_kcal": 2800,
            },
            tolerances={
                "protein": 10,
                "total_kcal": 100,
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": "/ai-tools/compare-dailyplan-to-targets/",
                    "payload": {
                        "dailyplan_id": 123,
                        "targets": {
                            "protein": 190,
                            "total_kcal": 2800,
                        },
                        "tolerances": {
                            "protein": 10,
                            "total_kcal": 100,
                        },
                    },
                }
            ],
        )

    def test_compare_dailyplan_to_targets_omits_empty_tolerances(self):
        result = compare_dailyplan_to_targets(
            client=self.client,
            dailyplan_id=123,
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
                    "api_path": "/ai-tools/compare-dailyplan-to-targets/",
                    "payload": {
                        "dailyplan_id": 123,
                        "targets": {
                            "protein": 190,
                        },
                    },
                }
            ],
        )

    def test_call_validation_tool_dispatches_compare(self):
        result = call_validation_tool(
            self.client,
            TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
            {
                "dailyplan_id": 123,
                "targets": {
                    "protein": 190,
                },
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls[0]["api_path"],
            "/ai-tools/compare-dailyplan-to-targets/",
        )

    def test_call_validation_tool_requires_dailyplan_id(self):
        result = call_validation_tool(
            self.client,
            TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
            {
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

    def test_call_validation_tool_requires_targets(self):
        result = call_validation_tool(
            self.client,
            TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
            {
                "dailyplan_id": 123,
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

    def test_call_validation_tool_rejects_unknown_validation_tool(self):
        result = call_validation_tool(
            self.client,
            "unknown_validation_tool",
            {},
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "unsupported_validation_tool:unknown_validation_tool",
        )
        self.assertEqual(
            self.client.calls,
            [],
        )


if __name__ == "__main__":
    unittest.main()