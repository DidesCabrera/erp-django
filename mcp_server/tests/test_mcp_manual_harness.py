import json
import unittest
from unittest.mock import patch

from myscoope_mcp.manual_harness import main


class MCPManualHarnessTests(unittest.TestCase):
    @patch(
        "sys.argv",
        [
            "manual_harness",
            "read_dailyplan",
            "--arguments",
            "{invalid json",
        ],
    )
    def test_manual_harness_rejects_invalid_json_arguments(self):
        exit_code = main()

        self.assertEqual(exit_code, 1)

    @patch(
        "sys.argv",
        [
            "manual_harness",
            "read_dailyplan",
            "--arguments",
            json.dumps(["not", "object"]),
        ],
    )
    def test_manual_harness_rejects_non_object_arguments(self):
        exit_code = main()

        self.assertEqual(exit_code, 1)

    @patch(
        "sys.argv",
        [
            "manual_harness",
            "apply_approved_proposal",
            "--arguments",
            json.dumps(
                {
                    "proposal_id": 999,
                }
            ),
        ],
    )
    def test_manual_harness_blocks_forbidden_tool_without_api_call(self):
        exit_code = main()

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()