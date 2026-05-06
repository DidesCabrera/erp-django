import json
import urllib.error
import urllib.request
from typing import Any

from myscoope_mcp.config import MCPServerConfig
from myscoope_mcp.contracts import MCPToolCallResult


class MyscoopeAPIClient:
    def __init__(self, config: MCPServerConfig):
        self.config = config

    def _build_url(self, api_path: str) -> str:
        if not api_path.startswith("/"):
            api_path = f"/{api_path}"

        return f"{self.config.normalized_api_base_url}{api_path}"

    def _build_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"

        return headers

    def call_ai_tool_api(
        self,
        api_path: str,
        payload: dict[str, Any] | None = None,
    ) -> MCPToolCallResult:
        url = self._build_url(api_path)
        body = json.dumps(payload or {}).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=body,
            headers=self._build_headers(),
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.config.request_timeout_seconds,
            ) as response:
                raw_body = response.read().decode("utf-8")
                data = json.loads(raw_body)

                return self._parse_adapter_response(data)

        except urllib.error.HTTPError as exc:
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "api_http_error",
                    "message": "The My Scoope API returned an HTTP error.",
                    "details": {
                        "status": exc.code,
                        "reason": exc.reason,
                    },
                },
            )

        except urllib.error.URLError as exc:
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "api_connection_error",
                    "message": "Could not connect to the My Scoope API.",
                    "details": {
                        "reason": str(exc.reason),
                    },
                },
            )

        except json.JSONDecodeError:
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "api_invalid_json_response",
                    "message": "The My Scoope API returned invalid JSON.",
                    "details": {},
                },
            )

    def _parse_adapter_response(
        self,
        data: dict[str, Any],
    ) -> MCPToolCallResult:
        if not isinstance(data, dict):
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "api_invalid_contract",
                    "message": "The My Scoope API response must be an object.",
                    "details": {},
                },
            )

        if set(data.keys()) != {"ok", "data", "error"}:
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "api_invalid_contract",
                    "message": "The My Scoope API response does not match ok/data/error contract.",
                    "details": {
                        "keys": sorted(data.keys()),
                    },
                },
            )

        if data["ok"] is True:
            if not isinstance(data["data"], dict):
                return MCPToolCallResult(
                    ok=False,
                    data={},
                    error={
                        "code": "api_invalid_success_contract",
                        "message": "Successful API responses must contain object data.",
                        "details": {},
                    },
                )

            return MCPToolCallResult(
                ok=True,
                data=data["data"],
                error=None,
            )

        if not isinstance(data["error"], dict):
            return MCPToolCallResult(
                ok=False,
                data={},
                error={
                    "code": "api_invalid_error_contract",
                    "message": "Failed API responses must contain an error object.",
                    "details": {},
                },
            )

        return MCPToolCallResult(
            ok=False,
            data={},
            error=data["error"],
        )