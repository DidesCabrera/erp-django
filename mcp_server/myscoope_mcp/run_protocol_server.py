import argparse
import os

from myscoope_mcp.protocol_server import (
    SERVER_NAME,
    assert_protocol_tool_surface_is_safe,
    create_mcp_server,
    get_protocol_allowed_tool_names,
)


DEFAULT_MCP_HTTP_HOST = "127.0.0.1"
DEFAULT_MCP_HTTP_PORT = 8001
STDIO_TRANSPORT = "stdio"
STREAMABLE_HTTP_TRANSPORT = "streamable-http"
HTTP_TRANSPORT_ALIAS = "http"


def _get_default_http_host() -> str:
    return os.getenv(
        "MYSCOOPE_MCP_HOST",
        DEFAULT_MCP_HTTP_HOST,
    )


def _get_default_http_port() -> int:
    raw_port = os.getenv(
        "MYSCOOPE_MCP_PORT",
        str(DEFAULT_MCP_HTTP_PORT),
    )

    return int(raw_port)


def _normalize_transport(transport: str) -> str:
    if transport == HTTP_TRANSPORT_ALIAS:
        return STREAMABLE_HTTP_TRANSPORT

    return transport


def _print_registered_tools() -> None:
    print(f"{SERVER_NAME} protocol server initialized safely.")
    print("Registered FastMCP MVP tools:")

    for tool_name in sorted(get_protocol_allowed_tool_names()):
        print(f"- {tool_name}")


def _print_http_runtime_info(
    host: str,
    port: int,
) -> None:
    print(f"{SERVER_NAME} HTTP MCP server starting.")
    print(f"MCP endpoint: http://{host}:{port}/mcp")
    print(f"Transport: {STREAMABLE_HTTP_TRANSPORT}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the My Scoope MCP protocol server."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Initialize and verify the server without starting the MCP runtime.",
    )
    parser.add_argument(
        "--transport",
        choices=[
            STDIO_TRANSPORT,
            STREAMABLE_HTTP_TRANSPORT,
            HTTP_TRANSPORT_ALIAS,
        ],
        default=os.getenv(
            "MYSCOOPE_MCP_TRANSPORT",
            STDIO_TRANSPORT,
        ),
        help="MCP transport to use. Defaults to stdio.",
    )
    parser.add_argument(
        "--host",
        default=_get_default_http_host(),
        help="HTTP host for remote MCP transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_get_default_http_port(),
        help="HTTP port for remote MCP transport.",
    )

    args = parser.parse_args()
    transport = _normalize_transport(args.transport)

    assert_protocol_tool_surface_is_safe()

    if transport == STREAMABLE_HTTP_TRANSPORT:
        server = create_mcp_server(
            host=args.host,
            port=args.port,
        )

        if args.check:
            _print_registered_tools()
            return

        _print_http_runtime_info(
            host=args.host,
            port=args.port,
        )

        server.run(
            transport=STREAMABLE_HTTP_TRANSPORT,
        )
        return

    server = create_mcp_server()

    if args.check:
        _print_registered_tools()
        return

    server.run(
        transport=STDIO_TRANSPORT,
    )


if __name__ == "__main__":
    main()