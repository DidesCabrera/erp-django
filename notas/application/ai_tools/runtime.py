from collections.abc import Callable
from typing import Any

from notas.application.ai_tools.errors import map_exception_to_tool_error
from notas.application.ai_tools.permissions import (
    ensure_authenticated_tool_user,
)
from notas.application.ai_tools.results import (
    AIToolResult,
    tool_success,
)


def run_ai_tool(
    tool_fn: Callable[..., dict[str, Any]],
    *args,
    user=None,
    require_auth: bool = True,
    **kwargs,
) -> AIToolResult:
    """
    Ejecuta una tool interna y normaliza su salida.

    Si require_auth=True, exige user autenticado antes de ejecutar la tool.

    La función recibida debe devolver un dict serializable.
    Si lanza una excepción conocida, se transforma en AIToolResult(ok=False).
    """
    try:
        if require_auth:
            ensure_authenticated_tool_user(user)

        data = tool_fn(
            *args,
            **kwargs,
        )

        return tool_success(
            data=data,
        )

    except Exception as exc:
        return map_exception_to_tool_error(exc)