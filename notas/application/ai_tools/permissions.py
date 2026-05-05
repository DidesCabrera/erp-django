def ensure_authenticated_tool_user(user) -> None:
    """
    AI tools internas siempre deben ejecutarse con un usuario autenticado.

    Esto evita que una futura API/MCP/tool se ejecute accidentalmente sin
    contexto de permisos.
    """
    if user is None:
        raise ValueError("tool_user_required")

    is_authenticated = getattr(
        user,
        "is_authenticated",
        False,
    )

    if not is_authenticated:
        raise ValueError("tool_user_not_authenticated")