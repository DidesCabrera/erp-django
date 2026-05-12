import unittest
from unittest.mock import patch

from myscoope_mcp.run_protocol_server import (
    _get_default_http_port,
    main as run_protocol_server_main,
)


class MCPLocalRuntimeTests(unittest.TestCase):
    def _assert_http_server_created_with_auth(
        self,
        mocked_create_mcp_server,
        *,
        expected_host: str,
        expected_port: int,
    ) -> None:
        mocked_create_mcp_server.assert_called_once()

        call_kwargs = mocked_create_mcp_server.call_args.kwargs

        self.assertEqual(
            call_kwargs["host"],
            expected_host,
        )
        self.assertEqual(
            call_kwargs["port"],
            expected_port,
        )
        self.assertIsNotNone(
            call_kwargs["token_verifier"],
        )
        self.assertIsNotNone(
            call_kwargs["auth_settings"],
        )

    def _get_printed_lines(
        self,
        mocked_print,
    ) -> list[str]:
        return [
            call.args[0]
            for call in mocked_print.call_args_list
        ]

    @patch(
        "sys.argv",
        [
            "run_protocol_server",
            "--check",
        ],
    )
    @patch("builtins.print")
    def test_check_mode_initializes_without_running_stdio_server(
        self,
        mocked_print,
    ):
        run_protocol_server_main()

        printed_lines = self._get_printed_lines(mocked_print)

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
    def test_default_mode_runs_stdio_server(
        self,
        mocked_create_mcp_server,
    ):
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
    @patch.dict(
        "os.environ",
        {
            "MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN": "external-token",
        },
        clear=True,
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

        self._assert_http_server_created_with_auth(
            mocked_create_mcp_server,
            expected_host="127.0.0.1",
            expected_port=8001,
        )

        fake_server.run.assert_called_once_with(
            transport="streamable-http",
        )

        printed_lines = self._get_printed_lines(mocked_print)

        self.assertIn(
            "my-scoope-mcp HTTP MCP server starting.",
            printed_lines,
        )
        self.assertIn(
            "MCP endpoint: http://127.0.0.1:8001/mcp",
            printed_lines,
        )
        self.assertIn(
            "Public MCP URL: http://127.0.0.1:8001/mcp",
            printed_lines,
        )
        self.assertIn(
            "Transport: streamable-http",
            printed_lines,
        )
        self.assertIn(
            "External MCP auth: enabled",
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
    @patch.dict(
        "os.environ",
        {
            "MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN": "external-token",
        },
        clear=True,
    )
    @patch("myscoope_mcp.run_protocol_server.create_mcp_server")
    def test_http_alias_runs_streamable_http_server(
        self,
        mocked_create_mcp_server,
    ):
        fake_server = mocked_create_mcp_server.return_value

        run_protocol_server_main()

        self._assert_http_server_created_with_auth(
            mocked_create_mcp_server,
            expected_host="127.0.0.1",
            expected_port=8001,
        )

        fake_server.run.assert_called_once_with(
            transport="streamable-http",
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
    @patch.dict(
        "os.environ",
        {},
        clear=True,
    )
    @patch("myscoope_mcp.run_protocol_server.create_mcp_server")
    def test_streamable_http_fails_without_external_auth_token(
        self,
        mocked_create_mcp_server,
    ):
        with self.assertRaises(RuntimeError):
            run_protocol_server_main()

        mocked_create_mcp_server.assert_not_called()

    @patch.dict(
        "os.environ",
        {},
        clear=True,
    )
    def test_default_http_port_falls_back_to_local_default(self):
        self.assertEqual(
            _get_default_http_port(),
            8001,
        )

    @patch.dict(
        "os.environ",
        {
            "PORT": "10000",
        },
        clear=True,
    )
    def test_default_http_port_reads_render_port(self):
        self.assertEqual(
            _get_default_http_port(),
            10000,
        )

    @patch.dict(
        "os.environ",
        {
            "PORT": "10000",
            "MYSCOOPE_MCP_PORT": "9001",
        },
        clear=True,
    )
    def test_explicit_mcp_port_overrides_render_port(self):
        self.assertEqual(
            _get_default_http_port(),
            9001,
        )

    @patch(
        "sys.argv",
        [
            "run_protocol_server",
            "--transport",
            "streamable-http",
        ],
    )
    @patch.dict(
        "os.environ",
        {
            "MYSCOOPE_MCP_HOST": "0.0.0.0",
            "PORT": "10000",
            "MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN": "external-token",
        },
        clear=True,
    )
    @patch("builtins.print")
    @patch("myscoope_mcp.run_protocol_server.create_mcp_server")
    def test_streamable_http_uses_remote_runtime_env_defaults(
        self,
        mocked_create_mcp_server,
        mocked_print,
    ):
        fake_server = mocked_create_mcp_server.return_value

        run_protocol_server_main()

        self._assert_http_server_created_with_auth(
            mocked_create_mcp_server,
            expected_host="0.0.0.0",
            expected_port=10000,
        )

        fake_server.run.assert_called_once_with(
            transport="streamable-http",
        )

        printed_lines = self._get_printed_lines(mocked_print)

        self.assertIn(
            "MCP endpoint: http://0.0.0.0:10000/mcp",
            printed_lines,
        )
        self.assertIn(
            "Public MCP URL: http://0.0.0.0:10000/mcp",
            printed_lines,
        )
        self.assertIn(
            "External MCP auth: enabled",
            printed_lines,
        )

    @patch(
        "sys.argv",
        [
            "run_protocol_server",
            "--transport",
            "streamable-http",
        ],
    )
    @patch.dict(
        "os.environ",
        {
            "MYSCOOPE_MCP_HOST": "0.0.0.0",
            "PORT": "10000",
            "MYSCOOPE_MCP_PUBLIC_URL": "https://mcp.myscoope.com",
            "MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN": "external-token",
        },
        clear=True,
    )
    @patch("builtins.print")
    @patch("myscoope_mcp.run_protocol_server.create_mcp_server")
    def test_streamable_http_prints_configured_public_url(
        self,
        mocked_create_mcp_server,
        mocked_print,
    ):
        fake_server = mocked_create_mcp_server.return_value

        run_protocol_server_main()

        self._assert_http_server_created_with_auth(
            mocked_create_mcp_server,
            expected_host="0.0.0.0",
            expected_port=10000,
        )

        fake_server.run.assert_called_once_with(
            transport="streamable-http",
        )

        printed_lines = self._get_printed_lines(mocked_print)

        self.assertIn(
            "MCP endpoint: http://0.0.0.0:10000/mcp",
            printed_lines,
        )
        self.assertIn(
            "Public MCP URL: https://mcp.myscoope.com/mcp",
            printed_lines,
        )


if __name__ == "__main__":
    unittest.main()