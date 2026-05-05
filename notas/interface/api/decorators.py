from functools import wraps

from django.contrib.auth.decorators import login_required

from notas.application.ai_tools.results import tool_error
from notas.interface.api.responses import (
    ai_tool_json_response,
    invalid_json_response,
    method_not_allowed_response,
    parse_json_body,
)


def ai_tool_api_view(view_func):
    """
    Decorador base para endpoints del API Adapter MVP.

    Responsabilidades:
    - exige login;
    - exige POST;
    - parsea JSON;
    - normaliza errores básicos del adapter;
    - deja request.ai_tool_payload disponible para la vista.
    """

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method != "POST":
            return method_not_allowed_response()

        try:
            request.ai_tool_payload = parse_json_body(request)
        except ValueError as exc:
            if str(exc) == "invalid_json":
                return invalid_json_response()

            return ai_tool_json_response(
                tool_error(
                    code=str(exc),
                    message="Request body is not valid for this endpoint.",
                ),
                status=400,
            )

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapper
    