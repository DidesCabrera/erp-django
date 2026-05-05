from notas.application.ai_tools.results import tool_success
from notas.interface.api.decorators import ai_tool_api_view
from notas.interface.api.responses import ai_tool_json_response


@ai_tool_api_view
def ai_tools_health(request):
    return ai_tool_json_response(
        tool_success(
            {
                "status": "ok",
                "adapter": "ai_tools_api",
            }
        )
    )