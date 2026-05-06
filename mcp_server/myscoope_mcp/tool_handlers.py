from typing import Any

from myscoope_mcp.client import MyscoopeAPIClient
from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.tools import (
    TOOL_LIST_USER_PROPOSALS,
    TOOL_READ_DAILYPLAN,
    TOOL_READ_PROPOSAL,
    get_tool_spec,
)


def read_dailyplan(
    client: MyscoopeAPIClient,
    dailyplan_id: int,
) -> MCPToolCallResult:
    spec = get_tool_spec(TOOL_READ_DAILYPLAN)

    return client.call_ai_tool_api(
        spec.api_path,
        {
            "dailyplan_id": dailyplan_id,
        },
    )


def read_proposal(
    client: MyscoopeAPIClient,
    proposal_id: int,
) -> MCPToolCallResult:
    spec = get_tool_spec(TOOL_READ_PROPOSAL)

    return client.call_ai_tool_api(
        spec.api_path,
        {
            "proposal_id": proposal_id,
        },
    )


def list_user_proposals(
    client: MyscoopeAPIClient,
) -> MCPToolCallResult:
    spec = get_tool_spec(TOOL_LIST_USER_PROPOSALS)

    return client.call_ai_tool_api(
        spec.api_path,
        {},
    )


READ_TOOL_HANDLERS = {
    TOOL_READ_DAILYPLAN: read_dailyplan,
    TOOL_READ_PROPOSAL: read_proposal,
    TOOL_LIST_USER_PROPOSALS: list_user_proposals,
}


def call_read_tool(
    client: MyscoopeAPIClient,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> MCPToolCallResult:
    arguments = arguments or {}

    if tool_name == TOOL_READ_DAILYPLAN:
        if "dailyplan_id" not in arguments:
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "missing_required_argument:dailyplan_id",
                    "message": "Missing required argument: dailyplan_id.",
                    "details": {},
                },
            )

        return read_dailyplan(
            client,
            arguments["dailyplan_id"],
        )

    if tool_name == TOOL_READ_PROPOSAL:
        if "proposal_id" not in arguments:
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "missing_required_argument:proposal_id",
                    "message": "Missing required argument: proposal_id.",
                    "details": {},
                },
            )

        return read_proposal(
            client,
            arguments["proposal_id"],
        )

    if tool_name == TOOL_LIST_USER_PROPOSALS:
        return list_user_proposals(client)

    return MCPToolCallResult(
        ok=False,
        data={},
        error={
            "code": f"unsupported_read_tool:{tool_name}",
            "message": "Unsupported MCP read tool.",
            "details": {},
        },
    )