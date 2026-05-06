import argparse

from myscoope_mcp.protocol_server import (
    SERVER_NAME,
    assert_protocol_tool_surface_is_safe,
    create_mcp_server,
    get_protocol_allowed_tool_names,
)


def _print_registered_tools() -> None:
    print(f"{SERVER_NAME} protocol server initialized safely.")
    print("Registered FastMCP MVP tools:")

    for tool_name in sorted(get_protocol_allowed_tool_names()):
        print(f"- {tool_name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the My Scoope MCP protocol server."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Initialize and verify the server without starting the MCP runtime.",
    )

    args = parser.parse_args()

    assert_protocol_tool_surface_is_safe()

    server = create_mcp_server()

    if args.check:
        _print_registered_tools()
        return

    server.run(transport="stdio")


if __name__ == "__main__":
    main()