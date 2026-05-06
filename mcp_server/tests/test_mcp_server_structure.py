import json
import unittest

from myscoope_mcp.config import (
    DEFAULT_API_BASE_URL,
    MCPServerConfig,
    load_config_from_env,
)
from myscoope_mcp.server import get_registered_tools


class MCPServerStructureTests(unittest.TestCase):
    def test_config_has_safe_defaults(self):
        config = load_config_from_env()

        self.assertIsInstance(config, MCPServerConfig)
        self.assertEqual(
            DEFAULT_API_BASE_URL,
            "http://127.0.0.1:8000/app",
        )
        self.assertTrue(
            config.normalized_api_base_url.startswith("http"),
        )

    def test_registered_tools_are_json_serializable(self):
        tools = get_registered_tools()

        self.assertIsInstance(tools, list)
        self.assertGreaterEqual(
            len(tools),
            1,
        )

        json.dumps(tools)

    def test_registered_tools_have_required_shape(self):
        tools = get_registered_tools()

        for tool in tools:
            self.assertEqual(
                set(tool.keys()),
                {
                    "name",
                    "description",
                    "api_path",
                    "input_schema",
                },
            )
            self.assertIsInstance(tool["name"], str)
            self.assertIsInstance(tool["description"], str)
            self.assertIsInstance(tool["api_path"], str)
            self.assertIsInstance(tool["input_schema"], dict)
            self.assertTrue(
                tool["api_path"].startswith("/ai-tools/"),
            )


if __name__ == "__main__":
    unittest.main()