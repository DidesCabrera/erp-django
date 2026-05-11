import unittest

from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.dispatcher import dispatch_tool_call
from myscoope_mcp.tool_handlers import (
    call_proposal_tool,
    create_validated_dailyplan_build_proposal,
)
from myscoope_mcp.tools import TOOL_CREATE_VALIDATED_DAILYPLAN_BUILD_PROPOSAL


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


class MCPDailyPlanBuildProposalToolTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeMyscoopeAPIClient()
        self.proposed_payload = {
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
                                    "food_id": 1,
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
                                    "food_id": 2,
                                    "quantity": 200,
                                },
                            ],
                        },
                    },
                ],
            },
        }

    def test_create_validated_dailyplan_build_proposal_calls_api_adapter(self):
        result = create_validated_dailyplan_build_proposal(
            self.client,
            dailyplan_id=128,
            title="Propuesta MCP - Día entrenamiento IA",
            summary="DailyPlan propuesto desde MCP.",
            targets={
                "protein": 190,
                "total_kcal": 2800,
            },
            proposed_payload=self.proposed_payload,
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": (
                        "/ai-tools/create-validated-dailyplan-build-proposal/"
                    ),
                    "payload": {
                        "dailyplan_id": 128,
                        "title": "Propuesta MCP - Día entrenamiento IA",
                        "summary": "DailyPlan propuesto desde MCP.",
                        "targets": {
                            "protein": 190,
                            "total_kcal": 2800,
                        },
                        "proposed_payload": self.proposed_payload,
                    },
                }
            ],
        )

    def test_call_proposal_tool_dispatches_create_validated_dailyplan_build_proposal(self):
        result = call_proposal_tool(
            self.client,
            TOOL_CREATE_VALIDATED_DAILYPLAN_BUILD_PROPOSAL,
            {
                "dailyplan_id": 128,
                "title": "Propuesta MCP - Día entrenamiento IA",
                "proposed_payload": self.proposed_payload,
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls,
            [
                {
                    "api_path": (
                        "/ai-tools/create-validated-dailyplan-build-proposal/"
                    ),
                    "payload": {
                        "dailyplan_id": 128,
                        "title": "Propuesta MCP - Día entrenamiento IA",
                        "summary": "",
                        "proposed_payload": self.proposed_payload,
                    },
                }
            ],
        )

    def test_dispatch_tool_call_routes_create_validated_dailyplan_build_proposal(self):
        result = dispatch_tool_call(
            client=self.client,
            tool_name=TOOL_CREATE_VALIDATED_DAILYPLAN_BUILD_PROPOSAL,
            arguments={
                "dailyplan_id": 128,
                "title": "Propuesta MCP - Día entrenamiento IA",
                "proposed_payload": self.proposed_payload,
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            self.client.calls[0]["api_path"],
            "/ai-tools/create-validated-dailyplan-build-proposal/",
        )


if __name__ == "__main__":
    unittest.main()