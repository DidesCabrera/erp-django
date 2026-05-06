import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from myscoope_mcp.contracts import MCPToolCallResult
from myscoope_mcp.protocol_server import (
    create_mcp_server,
    serialize_tool_result,
)
from myscoope_mcp.run_protocol_server import main as run_protocol_server_main


PROTOCOL_SERVER_PATH = Path(
    "mcp_server/myscoope_mcp/protocol_server.py"
)


REQUIRED_MCP_TOOL_FUNCTIONS = {
    "list_user_proposals",
    "read_dailyplan",
    "read_proposal",
    "compare_dailyplan_to_targets",
    "create_validated_dailyplan_proposal",
}


FORBIDDEN_TOOL_FUNCTIONS = {
    "apply_approved_proposal",
    "apply_proposal",
    "apply_validated_proposal",
    "delete_food",
    "delete_meal",
    "delete_dailyplan",
    "update_food",
    "update_meal",
    "update_dailyplan",
    "create_food",
    "create_meal",
    "create_dailyplan",
    "raw_sql",
    "raw_command_execution",
    "raw_model_mutation",
}


FORBIDDEN_IMPORT_PREFIXES = {
    "notas.domain",
    "notas.application.queries",
    "notas.application.services.commands",
}


class MCPProtocolWrapperContractTests(unittest.TestCase):
    def _source(self):
        return PROTOCOL_SERVER_PATH.read_text()

    def _tree(self):
        return ast.parse(
            self._source(),
        )

    def test_protocol_server_imports_no_forbidden_django_layers(self):
        tree = self._tree()

        imported_modules = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name)

            if isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

        for imported_module in imported_modules:
            for forbidden_prefix in FORBIDDEN_IMPORT_PREFIXES:
                self.assertFalse(
                    imported_module.startswith(forbidden_prefix),
                    msg=f"Forbidden import found: {imported_module}",
                )

    def test_required_mcp_tool_functions_exist(self):
        tree = self._tree()

        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }

        for function_name in REQUIRED_MCP_TOOL_FUNCTIONS:
            self.assertIn(
                function_name,
                function_names,
            )

    def test_forbidden_mcp_tool_functions_do_not_exist(self):
        tree = self._tree()

        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }

        for function_name in FORBIDDEN_TOOL_FUNCTIONS:
            self.assertNotIn(
                function_name,
                function_names,
            )

    def test_each_required_tool_routes_through_dispatcher(self):
        source = self._source()

        self.assertGreaterEqual(
            source.count("dispatch_tool_call("),
            5,
        )

        for function_name in REQUIRED_MCP_TOOL_FUNCTIONS:
            self.assertIn(
                f"def {function_name}",
                source,
            )

    def test_protocol_wrapper_does_not_accept_user_id_as_argument(self):
        source = self._source()

        forbidden_snippets = [
            "user_id:",
            '"user_id"',
            "'user_id'",
        ]

        for snippet in forbidden_snippets:
            self.assertNotIn(
                snippet,
                source,
            )

    def test_protocol_wrapper_mentions_no_final_application_for_proposal_tool(self):
        source = self._source()

        self.assertIn(
            "It does not apply final changes.",
            source,
        )

    def test_create_mcp_server_smoke_test(self):
        server = create_mcp_server()

        self.assertEqual(
            server.name,
            "my-scoope-mcp",
        )

    def test_serialize_tool_result_success_contract(self):
        result = MCPToolCallResult(
            ok=True,
            data={
                "value": 123,
            },
            error=None,
        )

        self.assertEqual(
            serialize_tool_result(result),
            {
                "ok": True,
                "data": {
                    "value": 123,
                },
                "error": None,
            },
        )

    def test_serialize_tool_result_error_contract(self):
        result = MCPToolCallResult(
            ok=False,
            data={},
            error={
                "code": "forbidden_mcp_tool:apply_approved_proposal",
                "message": "This MCP tool is explicitly forbidden.",
                "details": {},
            },
        )

        self.assertEqual(
            serialize_tool_result(result),
            {
                "ok": False,
                "data": {},
                "error": {
                    "code": "forbidden_mcp_tool:apply_approved_proposal",
                    "message": "This MCP tool is explicitly forbidden.",
                    "details": {},
                },
            },
        )

    @patch(
        "sys.argv",
        [
            "run_protocol_server",
            "--check",
        ],
    )
    @patch("builtins.print")
    def test_run_protocol_server_check_mode_prints_registered_tools(self, mocked_print):
        run_protocol_server_main()

        printed_lines = [
            call.args[0]
            for call in mocked_print.call_args_list
        ]

        self.assertIn(
            "my-scoope-mcp protocol server initialized safely.",
            printed_lines,
        )
        self.assertIn(
            "- list_user_proposals",
            printed_lines,
        )
        self.assertIn(
            "- read_dailyplan",
            printed_lines,
        )
        self.assertIn(
            "- read_proposal",
            printed_lines,
        )
        self.assertIn(
            "- compare_dailyplan_to_targets",
            printed_lines,
        )
        self.assertIn(
            "- create_validated_dailyplan_proposal",
            printed_lines,
        )

if __name__ == "__main__":
    unittest.main()