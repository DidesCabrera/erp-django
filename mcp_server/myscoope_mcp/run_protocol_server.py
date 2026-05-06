from myscoope_mcp.protocol_server import (
    assert_protocol_tool_surface_is_safe,
    create_mcp_server,
)


def main() -> None:
    assert_protocol_tool_surface_is_safe()

    server = create_mcp_server()

    print(f"{server.name} protocol server initialized safely.")
    print("Registered initial FastMCP tools.")
    print("To run the server, use this module from a protocol runtime in the next blocks.")


if __name__ == "__main__":
    main()