from myscoope_mcp.tools import list_allowed_tool_specs


def get_registered_tools() -> list[dict]:
    """
    Returns the current MCP tool registry as dictionaries.

    This is not a real MCP protocol server yet.
    It is a safe placeholder used to protect the allowed tool surface
    before adding protocol-specific dependencies.
    """
    return [
        tool.as_dict()
        for tool in list_allowed_tool_specs()
    ]
    