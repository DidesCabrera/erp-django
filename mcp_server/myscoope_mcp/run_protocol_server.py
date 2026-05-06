from myscoope_mcp.protocol_server import (
    assert_protocol_tool_surface_is_safe,
    create_mcp_server,
)


def main() -> None:
    assert_protocol_tool_surface_is_safe()

    server = create_mcp_server()

    print(f"{server.name} protocol server initialized safely.")
    print("Registered FastMCP MVP tools:")
    print("- list_user_proposals")
    print("- read_dailyplan")
    print("- read_proposal")
    print("- compare_dailyplan_to_targets")
    print("- create_validated_dailyplan_proposal")


if __name__ == "__main__":
    main()