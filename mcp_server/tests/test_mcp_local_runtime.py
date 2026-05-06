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

        fake_server.run.assert_called_once_with(
            transport="stdio",
        )


if __name__ == "__main__":
    unittest.main()
    