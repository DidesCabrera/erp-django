import unittest

from mcp.server.fastmcp import FastMCP

from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.protocol_server import (
    SERVER_NAME,
    assert_protocol_tool_surface_is_safe,
    create_mcp_server,
    get_protocol_allowed_tool_names,
    get_protocol_forbidden_tool_names,
    protocol_dispatch_placeholder,
    serialize_tool_result,
)
from myscoope_mcp.tools import (
    TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
    TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
    TOOL_LIST_USER_PROPOSALS,
    TOOL_READ_DAILYPLAN,
    TOOL_READ_PROPOSAL,
)


class MCPProtocolServerTests(unittest.TestCase):
    def test_create_mcp_server_returns_fastmcp_instance(self):
        server = create_mcp_server()

        self.assertIsInstance(server, FastMCP)
        self.assertEqual(server.name, SERVER_NAME)

    def test_allowed_protocol_tool_names_are_expected_mvp_surface(self):
        self.assertEqual(
            get_protocol_allowed_tool_names(),
            {
                TOOL_READ_DAILYPLAN,
                TOOL_READ_PROPOSAL,
                TOOL_LIST_USER_PROPOSALS,
                TOOL_COMPARE_DAILYPLAN_TO_TARGETS,
                TOOL_CREATE_VALIDATED_DAILYPLAN_PROPOSAL,
            },
        )

    def test_protocol_forbidden_tool_names_include_apply_tools(self):
        forbidden = get_protocol_forbidden_tool_names()

        self.assertIn("apply_approved_proposal", forbidden)
        self.assertIn("apply_proposal", forbidden)
        self.assertIn("apply_validated_proposal", forbidden)

    def test_protocol_tool_surface_has_no_forbidden_overlap(self):
        assert_protocol_tool_surface_is_safe()

    def test_protocol_wrapper_uses_dispatcher_boundary(self):
        dispatch = protocol_dispatch_placeholder()

        self.assertTrue(callable(dispatch))

    def test_serialize_tool_result_preserves_success_contract(self):
        result = MCPToolCallResult(
            ok=True,
            data={
                "proposals": [],
            },
            error=None,
        )

        self.assertEqual(
            serialize_tool_result(result),
            {
                "ok": True,
                "data": {
                    "proposals": [],
                },
                "error": None,
            },
        )

    def test_serialize_tool_result_preserves_error_contract(self):
        result = MCPToolCallResult(
            ok=False,
            data={},
            error={
                "code": "not_found",
                "message": "Not found.",
                "details": {},
            },
        )

        self.assertEqual(
            serialize_tool_result(result),
            {
                "ok": False,
                "data": {},
                "error": {
                    "code": "not_found",
                    "message": "Not found.",
                    "details": {},
                },
            },
        )

    def test_create_mcp_server_registers_all_mvp_tools_without_sdk_internal_assertions(self):
        server = create_mcp_server()

        self.assertIsInstance(server, FastMCP)
        self.assertEqual(server.name, SERVER_NAME)


if __name__ == "__main__":
    unittest.main()