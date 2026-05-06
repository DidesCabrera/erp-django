from myscoope_mcp.protocol_server import (
    assert_protocol_tool_surface_is_safe,
    create_mcp_server,
)


def main() -> None:
    assert_protocol_tool_surface_is_safe()

    server = create_mcp_server()

    # We do not call server.run() in this block.
    # This entrypoint is only a safe import/startup verification point.
    print(f"{server.name} protocol server initialized safely.")


if __name__ == "__main__":
    main()