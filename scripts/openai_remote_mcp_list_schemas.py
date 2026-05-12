import os
from openai import OpenAI


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1")
MCP_URL = os.environ["MYSCOOPE_REMOTE_MCP_URL"]
MCP_TOKEN = os.environ["MYSCOOPE_MCP_EXTERNAL_AUTH_TOKEN"]

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
                    "list_food_catalog",
                    "create_validated_meal_proposal",
                    "create_validated_dailyplan_build_proposal",
                ],
                "require_approval": "never",
            }
        ],
        input=(
            "List the available My Scoope MCP tools and describe the exact input schema "
            "for these tools only: list_food_catalog, create_validated_meal_proposal, "
            "create_validated_dailyplan_build_proposal. Do not call proposal creation tools. "
            "Only inspect/list schemas."
        ),
    )

    print(response.output_text or "[empty output_text]")
    print("\n--- Raw output items ---")
    for item in response.output:
        print(item)


if __name__ == "__main__":
    main()