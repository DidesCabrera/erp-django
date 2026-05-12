import os
from openai import OpenAI


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1")
MCP_URL = os.environ["MYSCOOPE_REMOTE_MCP_URL"]
MCP_TOKEN = os.environ["MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN"]
DAILYPLAN_ID = os.environ["DAILYPLAN_ID"]


client = OpenAI()


def main() -> None:
    response = client.responses.create(
        model=OPENAI_MODEL,
        tools=[
            {
                "type": "mcp",
                "server_label": "myscoope",
                "server_url": MCP_URL,
                "headers": {
                    "Authorization": f"Bearer {MCP_TOKEN}",
                },
                "allowed_tools": [
                    "read_dailyplan",
                    "compare_dailyplan_to_targets",
                    "list_user_proposals",
                    "read_proposal",
                ],
                "require_approval": "never",
            }
        ],
        input=(
            "You are testing a remote MCP connection to My Scoope.\n"
            "Use the available MCP tools to do exactly this:\n"
            f"1. Read dailyplan_id={DAILYPLAN_ID}.\n"
            "2. Compare it against targets protein=190 and total_kcal=2800, "
            "with tolerances protein=10 and total_kcal=100.\n"
            "3. Do not create proposals in this first smoke test.\n"
            "4. Summarize whether the MCP calls worked.\n"
        ),
    )

    print(response.output_text)
    print("\n--- Raw output items ---")
    for item in response.output:
        print(item)


if __name__ == "__main__":
    main()