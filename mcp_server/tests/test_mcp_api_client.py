import json
import unittest
from unittest.mock import patch

from myscoope_mcp.client import MyscoopeAPIClient
from myscoope_mcp.config import MCPServerConfig


class FakeHTTPResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class MyscoopeAPIClientTests(unittest.TestCase):
    def setUp(self):
        self.config = MCPServerConfig(
            api_base_url="http://testserver/app/",
            auth_token="test-token",
            request_timeout_seconds=5,
        )
        self.client = MyscoopeAPIClient(self.config)

    def test_build_url_normalizes_base_and_path(self):
        self.assertEqual(
            self.client._build_url("/ai-tools/read-dailyplan/"),
            "http://testserver/app/ai-tools/read-dailyplan/",
        )

        self.assertEqual(
            self.client._build_url("ai-tools/read-dailyplan/"),
            "http://testserver/app/ai-tools/read-dailyplan/",
        )

    def test_build_headers_includes_auth_token(self):
        headers = self.client._build_headers()

        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer test-token")

    def test_build_headers_without_auth_token(self):
        client = MyscoopeAPIClient(
            MCPServerConfig(
                api_base_url="http://testserver/app",
                auth_token=None,
            )
        )

        headers = client._build_headers()

        self.assertNotIn("Authorization", headers)

    @patch("urllib.request.urlopen")
    def test_call_ai_tool_api_returns_success_contract(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeHTTPResponse(
            {
                "ok": True,
                "data": {
                    "dailyplan": {
                        "id": 123,
                    },
                },
                "error": None,
            }
        )

        result = self.client.call_ai_tool_api(
            "/ai-tools/read-dailyplan/",
            {
                "dailyplan_id": 123,
            },
        )

        data = result.as_dict()

        self.assertTrue(data["ok"])
        self.assertEqual(
            data["data"],
            {
                "dailyplan": {
                    "id": 123,
                },
            },
        )
        self.assertIsNone(data["error"])

    @patch("urllib.request.urlopen")
    def test_call_ai_tool_api_returns_error_contract(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeHTTPResponse(
            {
                "ok": False,
                "data": {},
                "error": {
                    "code": "not_found",
                    "message": "Not found.",
                    "details": {},
                },
            }
        )

        result = self.client.call_ai_tool_api(
            "/ai-tools/read-dailyplan/",
            {
                "dailyplan_id": 999,
            },
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(data["data"], {})
        self.assertEqual(data["error"]["code"], "not_found")

    def test_parse_adapter_response_rejects_invalid_shape(self):
        result = self.client._parse_adapter_response(
            {
                "unexpected": True,
            }
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(data["error"]["code"], "api_invalid_contract")

    def test_parse_adapter_response_rejects_invalid_success_data(self):
        result = self.client._parse_adapter_response(
            {
                "ok": True,
                "data": [],
                "error": None,
            }
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "api_invalid_success_contract",
        )

    def test_parse_adapter_response_rejects_invalid_error_data(self):
        result = self.client._parse_adapter_response(
            {
                "ok": False,
                "data": {},
                "error": None,
            }
        )

        data = result.as_dict()

        self.assertFalse(data["ok"])
        self.assertEqual(
            data["error"]["code"],
            "api_invalid_error_contract",
        )


if __name__ == "__main__":
    unittest.main()