import json

from django.http import JsonResponse

from notas.application.ai_tools.results import (
    AIToolResult,
    tool_error,
)


def ai_tool_json_response(
    result: AIToolResult,
    *,
    status: int = 200,
) -> JsonResponse:
    return JsonResponse(
        result.as_dict(),
        status=status,
    )


def invalid_json_response() -> JsonResponse:
    return ai_tool_json_response(
        tool_error(
            code="invalid_json",
            message="Request body must be valid JSON.",
        ),
        status=400,
    )


def method_not_allowed_response() -> JsonResponse:
    return ai_tool_json_response(
        tool_error(
            code="method_not_allowed",
            message="This endpoint only accepts POST requests.",
        ),
        status=405,
    )


def parse_json_body(request) -> dict:
    if not request.body:
        return {}

    try:
        payload = json.loads(
            request.body.decode("utf-8"),
        )
    except json.JSONDecodeError:
        raise ValueError("invalid_json")

    if not isinstance(payload, dict):
        raise ValueError("json_body_must_be_object")

    return payload

def internal_api_auth_error_response(error, status: int = 401):
    return JsonResponse(
        {
            "ok": False,
            "data": {},
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
            },
        },
        status=status,
    )