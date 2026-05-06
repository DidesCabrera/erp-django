import unittest

from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.tool_handlers import (
    call_read_tool,
    list_user_proposals,
    read_dailyplan,
    read_proposal,
)
from myscoope_mcp.tools import (
    TOOL_LIST_USER_PROPOSALS,
    TOOL_READ_DAILYPLAN,
    TOOL_READ_PROPOSAL,
)


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


class MCPReadToolHandlerTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeMyscoopeAPIClient()

    def test_read_dailyplan_calls_api_adapter(self):
        result = read_dailyplan(
            self.client,
            dailyplan_id=123,
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": "/ai-tools/read-dailyplan/",
                    "payload": {
                        "dailyplan_id": 123,
                    },
                }
            ],
        )

    def test_read_proposal_calls_api_adapter(self):
        result = read_proposal(
            self.client,
            proposal_id=456,
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": "/ai-tools/read-proposal/",
                    "payload": {
                        "proposal_id": 456,
                    },
                }
            ],
        )

    def test_list_user_proposals_calls_api_adapter(self):
        result = list_user_proposals(
            self.client,
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": "/ai-tools/list-user-proposals/",
                    "payload": {},
                }
            ],
        )

    def test_call_read_tool_dispatches_read_dailyplan(self):
        result = call_read_tool(
            self.client,
            TOOL_READ_DAILYPLAN,
            {
                "dailyplan_id": 123,
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls[0]["api_path"],
            "/ai-tools/read-dailyplan/",
        )

    def test_call_read_tool_dispatches_read_proposal(self):
        result = call_read_tool(
            self.client,
            TOOL_READ_PROPOSAL,
            {
                "proposal_id": 456,
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls[0]["api_path"],
            "/ai-tools/read-proposal/",
        )

    def test_call_read_tool_dispatches_list_user_proposals(self):
        result = call_read_tool(
            self.client,
            TOOL_LIST_USER_PROPOSALS,
            {},
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls[0]["api_path"],
            "/ai-tools/list-user-proposals/",
        )

    def test_call_read_tool_requires_dailyplan_id(self):
        result = call_read_tool(
            self.client,
            TOOL_READ_DAILYPLAN,
            {},
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

    def test_call_read_tool_requires_proposal_id(self):
        result = call_read_tool(
            self.client,
            TOOL_READ_PROPOSAL,
            {},
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "missing_required_argument:proposal_id",
        )
        self.assertEqual(
            self.client.calls,
            [],
        )

    def test_call_read_tool_rejects_unknown_read_tool(self):
        result = call_read_tool(
            self.client,
            "unknown_read_tool",
            {},
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "unsupported_read_tool:unknown_read_tool",
        )
        self.assertEqual(
            self.client.calls,
            [],
        )


if __name__ == "__main__":
    unittest.main()
    