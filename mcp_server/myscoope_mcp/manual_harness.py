import argparse
import json
import sys

from myscoope_mcp.client import MyscoopeAPIClient
from myscoope_mcp.config import load_config_from_env
from myscoope_mcp.dispatcher import dispatch_tool_call


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manual harness for My Scoope MCP tool calls."
    )
    parser.add_argument(
        "tool_name",
        help="Name of the MCP tool to call.",
    )
    parser.add_argument(
        "--arguments",
        default="{}",
        help="JSON object with tool arguments.",
    )

    args = parser.parse_args()

    try:
        arguments = json.loads(args.arguments)
    except json.JSONDecodeError:
        print(
            json.dumps(
                {
                    "ok": False,
                    "data": {},
                    "error": {
                        "code": "invalid_arguments_json",
                        "message": "Arguments must be valid JSON.",
                        "details": {},
                    },
                },
                indent=2,
            )
        )
        return 1

    if not isinstance(arguments, dict):
        print(
            json.dumps(
                {
                    "ok": False,
                    "data": {},
                    "error": {
                        "code": "arguments_must_be_object",
                        "message": "Arguments must be a JSON object.",
                        "details": {},
                    },
                },
                indent=2,
            )
        )
        return 1

    config = load_config_from_env()
    client = MyscoopeAPIClient(config)

    result = dispatch_tool_call(
        client=client,
        tool_name=args.tool_name,
        arguments=arguments,
    )

    print(
        json.dumps(
            result.as_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )

    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())