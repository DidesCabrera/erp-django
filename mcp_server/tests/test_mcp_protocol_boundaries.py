import ast
from pathlib import Path
import unittest


PROTOCOL_SERVER_PATH = Path(
    "mcp_server/myscoope_mcp/protocol_server.py"
)


FORBIDDEN_IMPORT_PREFIXES = {
    "notas.domain",
    "notas.application.queries",
    "notas.application.services.commands",
}


REQUIRED_TOOL_FUNCTIONS = {
    "list_user_proposals",
    "read_dailyplan",
    "read_proposal",
}


class MCPProtocolBoundaryTests(unittest.TestCase):
    def _parse_protocol_server(self):
        return ast.parse(
            PROTOCOL_SERVER_PATH.read_text(),
        )

    def test_protocol_server_does_not_import_forbidden_django_layers(self):
        tree = self._parse_protocol_server()

        imported_modules = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name)

            if isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_modules.add(node.module)

        for imported_module in imported_modules:
            for forbidden_prefix in FORBIDDEN_IMPORT_PREFIXES:
                self.assertFalse(
                    imported_module.startswith(forbidden_prefix),
                    msg=(
                        f"Forbidden import found in protocol server: "
                        f"{imported_module}"
                    ),
                )

    def test_protocol_server_uses_dispatcher_boundary(self):
        source = PROTOCOL_SERVER_PATH.read_text()

        self.assertIn(
            "dispatch_tool_call",
            source,
        )

    def test_protocol_server_registers_required_read_tools(self):
        tree = self._parse_protocol_server()

        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }

        for tool_name in REQUIRED_TOOL_FUNCTIONS:
            self.assertIn(
                tool_name,
                function_names,
            )

    def test_registered_read_tools_call_dispatcher(self):
        source = PROTOCOL_SERVER_PATH.read_text()

        checks = [
            (
                "list_user_proposals",
                "TOOL_LIST_USER_PROPOSALS",
            ),
            (
                "read_dailyplan",
                "TOOL_READ_DAILYPLAN",
            ),
            (
                "read_proposal",
                "TOOL_READ_PROPOSAL",
            ),
        ]

        for function_name, tool_constant in checks:
            self.assertIn(
                f"def {function_name}",
                source,
            )
            self.assertIn(
                tool_constant,
                source,
            )

        self.assertGreaterEqual(
            source.count("dispatch_tool_call("),
            3,
        )

    def test_protocol_server_does_not_expose_apply_tool_names(self):
        source = PROTOCOL_SERVER_PATH.read_text()

        forbidden_snippets = [
            "@server.tool()\n    def apply_approved_proposal",
            "@server.tool()\n    def apply_proposal",
            "@server.tool()\n    def apply_validated_proposal",
        ]

        for snippet in forbidden_snippets:
            self.assertNotIn(
                snippet,
                source,
            )

    def test_protocol_server_does_not_accept_user_id_argument(self):
        source = PROTOCOL_SERVER_PATH.read_text()

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


if __name__ == "__main__":
    unittest.main()