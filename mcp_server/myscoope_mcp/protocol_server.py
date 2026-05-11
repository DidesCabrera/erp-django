from typing import Any

from mcp.server.fastmcp import FastMCP

from myscoope_mcp.client import MyscoopeAPIClient
from myscoope_mcp.config import load_config_from_env
from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.dispatcher import dispatch_tool_call
from myscoope_mcp.tools import (
    FORBIDDEN_TOOL_NAMES,
    TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
    TOOL_CREATE_VALIDATED_MEAL_PROPOSAL,
    TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
    TOOL_LIST_USER_PROPOSALS,
    TOOL_READ_DAILYPLAN,
    TOOL_READ_PROPOSAL,
    TOOL_LIST_FOOD_CATALOG,
)


SERVER_NAME = "my-scoope-mcp"


def create_api_client() -> MyscoopeAPIClient:
    config = load_config_from_env()

    return MyscoopeAPIClient(config)


def serialize_tool_result(
    result: MCPToolCallResult,
) -> dict[str, Any]:
    """
    Preserve the My Scoope ok/data/error contract for MCP responses.
    """
    return result.as_dict()


def create_mcp_server() -> FastMCP:
    """
    Create the real MCP protocol server.

    Boundary:
    - This module may import FastMCP.
    - This module may import the MCP dispatcher.
    - This module may create MyscoopeAPIClient.
    - This module must not import Django models, queries or commands.
    """
    assert_protocol_tool_surface_is_safe()

    server = FastMCP(SERVER_NAME)

    register_mcp_tools(server)

    return server


def register_mcp_tools(server: FastMCP) -> None:
    """
    Register real MCP tools.

    Every tool routes through dispatch_tool_call.
    This keeps the protocol wrapper thin and prevents bypassing the
    API Adapter / Internal AI Tools boundaries.
    """

    @server.tool()
    def list_user_proposals() -> dict[str, Any]:
        """
        List proposals visible to the authenticated My Scoope API context.
        """
        client = create_api_client()

        result = dispatch_tool_call(
            client=client,
            tool_name=TOOL_LIST_USER_PROPOSALS,
            arguments={},
        )

        return serialize_tool_result(result)


    @server.tool()
    def list_food_catalog(
        search: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        List readable foods available for AI/MCP nutrition planning.

        This tool is read-only.
        It does not create foods, meals or dailyplans.
        """
        client = create_api_client()

        arguments = {
            "limit": limit,
        }

        if search is not None:
            arguments["search"] = search

        result = dispatch_tool_call(
            client=client,
            tool_name=TOOL_LIST_FOOD_CATALOG,
            arguments=arguments,
        )

        return serialize_tool_result(result)


    @server.tool()
    def read_dailyplan(dailyplan_id: int) -> dict[str, Any]:
        """
        Read a DailyPlan available to the authenticated My Scoope API context.
        """
        client = create_api_client()

        result = dispatch_tool_call(
            client=client,
            tool_name=TOOL_READ_DAILYPLAN,
            arguments={
                "dailyplan_id": dailyplan_id,
            },
        )

        return serialize_tool_result(result)

    @server.tool()
    def read_proposal(proposal_id: int) -> dict[str, Any]:
        """
        Read a NutritionProposal available to the authenticated My Scoope API context.
        """
        client = create_api_client()

        result = dispatch_tool_call(
            client=client,
            tool_name=TOOL_READ_PROPOSAL,
            arguments={
                "proposal_id": proposal_id,
            },
        )

        return serialize_tool_result(result)

    @server.tool()
    def compare_dailyplan_to_targets(
        dailyplan_id: int,
        targets: dict[str, Any],
        tolerances: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Compare a DailyPlan against nutritional targets.

        This tool only validates and compares.
        It does not modify the DailyPlan.
        """
        client = create_api_client()

        arguments = {
            "dailyplan_id": dailyplan_id,
            "targets": targets,
        }

        if tolerances is not None:
            arguments["tolerances"] = tolerances

        result = dispatch_tool_call(
            client=client,
            tool_name=TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
            arguments=arguments,
        )

        return serialize_tool_result(result)

    @server.tool()
    def create_validated_meal_proposal(
        dailyplan_id: int,
        title: str,
        proposed_payload: dict[str, Any],
        targets: dict[str, Any] | None = None,
        summary: str = "",
    ) -> dict[str, Any]:
        """
        Create a reviewable meal proposal from a rich create_meal payload.

        This tool does not create a final Meal.
        It only creates a NutritionProposal pending human review.
        """
        client = create_api_client()

        arguments = {
            "dailyplan_id": dailyplan_id,
            "title": title,
            "summary": summary,
            "proposed_payload": proposed_payload,
        }

        if targets is not None:
            arguments["targets"] = targets

        result = dispatch_tool_call(
            client=client,
            tool_name=TOOL_CREATE_VALIDATED_MEAL_PROPOSAL,
            arguments=arguments,
        )

        return serialize_tool_result(result)



    @server.tool()
    def create_validated_dailyplan_proposal(
        dailyplan_id: int,
        title: str,
        targets: dict[str, Any],
        proposed_payload: dict[str, Any] | None = None,
        tolerances: dict[str, Any] | None = None,
        summary: str = "",
    ) -> dict[str, Any]:
        """
        Create a validated NutritionProposal for human review.

        This tool creates a proposal.
        It does not approve it.
        It does not apply final changes.
        """
        client = create_api_client()

        arguments = {
            "dailyplan_id": dailyplan_id,
            "title": title,
            "targets": targets,
        }

        if summary:
            arguments["summary"] = summary

        if proposed_payload is not None:
            arguments["proposed_payload"] = proposed_payload

        if tolerances is not None:
            arguments["tolerances"] = tolerances

        result = dispatch_tool_call(
            client=client,
            tool_name=TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
            arguments=arguments,
        )

        return serialize_tool_result(result)


def get_protocol_allowed_tool_names() -> set[str]:
    """
    Tool names allowed to be exposed by the real MCP protocol wrapper.
    """
    return {
        TOOL_READ_DAILYPLAN,
        TOOL_READ_PROPOSAL,
        TOOL_LIST_USER_PROPOSALS,
        TOOL_LIST_FOOD_CATALOG,
        TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
        TOOL_CREATE_VALIDATED_MEAL_PROPOSAL,
        TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
    }


def get_protocol_forbidden_tool_names() -> set[str]:
    """
    Explicitly forbidden tool names at the protocol wrapper boundary.
    """
    return set(FORBIDDEN_TOOL_NAMES)


def assert_protocol_tool_surface_is_safe() -> None:
    """
    Guardrail to ensure the protocol wrapper never exposes forbidden tools.
    """
    allowed = get_protocol_allowed_tool_names()
    forbidden = get_protocol_forbidden_tool_names()

    overlap = allowed.intersection(forbidden)

    if overlap:
        raise RuntimeError(
            f"Forbidden MCP tools cannot be exposed: {sorted(overlap)}"
        )


def protocol_dispatch_placeholder():
    """
    Placeholder reference proving that the protocol wrapper depends on
    dispatch_tool_call as the routing boundary.
    """
    return dispatch_tool_call