from collections.abc import Callable
from typing import Any

from notas.application.ai_tools.errors import map_exception_to_tool_error
from notas.application.ai_tools.results import (
    AIToolResult,
    tool_success,
)


def run_ai_tool(
    tool_fn: Callable[..., dict[str, Any]],
    *args,
    **kwargs,
) -> AIToolResult:
    """
    Ejecuta una tool interna y normaliza su salida.

    La función recibida debe devolver un dict serializable.
    Si lanza una excepción conocida, se transforma en AIToolResult(ok=False).
    """
    try:
        data = tool_fn(
            *args,
            **kwargs,
        )

        return tool_success(
            data=data,
        )

    except Exception as exc:
        return map_exception_to_tool_error(exc)