import unittest
from unittest.mock import patch

from myscoope_mcp.run_protocol_server import main as run_protocol_server_main


class MCPLocalRuntimeTests(unittest.TestCase):
    @patch(
        "sys.argv",
        [
            "run_protocol_server",
            "--check",
        ],
    )
    @patch("builtins.print")
    def test_check_mode_initializes_without_running_stdio_server(self, mocked_print):
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

    @patch(
        "sys.argv",
        [
            "run_protocol_server",
        ],
    )
    @patch("myscoope_mcp.run_protocol_server.create_mcp_server")
    def test_default_mode_runs_stdio_server(self, mocked_create_mcp_server):
        fake_server = mocked_create_mcp_server.return_value

        run_protocol_server_main()

        mocked_create_mcp_server.assert_called_once_with()

        fake_server.run.assert_called_once_with(
            transport="stdio",
        )

    @patch(
        "sys.argv",
        [
            "run_protocol_server",
            "--transport",
            "streamable-http",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
        ],
    )
    @patch("builtins.print")
    @patch("myscoope_mcp.run_protocol_server.create_mcp_server")
    def test_streamable_http_mode_runs_http_server(
        self,
        mocked_create_mcp_server,
        mocked_print,
    ):
        fake_server = mocked_create_mcp_server.return_value

        run_protocol_server_main()

        mocked_create_mcp_server.assert_called_once_with(
            host="127.0.0.1",
            port=8001,
        )

        fake_server.run.assert_called_once_with(
            transport="streamable-http",
        )

        printed_lines = [
            call.args[0]
            for call in mocked_print.call_args_list
        ]

        self.assertIn(
            "my-scoope-mcp HTTP MCP server starting.",
            printed_lines,
        )
        self.assertIn(
            "MCP endpoint: http://127.0.0.1:8001/mcp",
            printed_lines,
        )
        self.assertIn(
            "Transport: streamable-http",
            printed_lines,
        )

    @patch(
        "sys.argv",
        [
            "run_protocol_server",
            "--transport",
            "http",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
        ],
    )
    @patch("myscoope_mcp.run_protocol_server.create_mcp_server")
    def test_http_alias_runs_streamable_http_server(
        self,
        mocked_create_mcp_server,
    ):
        fake_server = mocked_create_mcp_server.return_value

        run_protocol_server_main()

        mocked_create_mcp_server.assert_called_once_with(
            host="127.0.0.1",
            port=8001,
        )

        fake_server.run.assert_called_once_with(
            transport="streamable-http",
        )


if __name__ == "__main__":
    unittest.main()