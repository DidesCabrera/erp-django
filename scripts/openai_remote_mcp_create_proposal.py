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
                    "create_validated_dailyplan_proposal",
                    "list_user_proposals",
                    "read_proposal",
                ],
                "require_approval": "never",
            }
        ],
        input=(
            "You are an external AI connected to My Scoope through remote MCP.\n"
            "\n"
            "Follow this exact safe workflow:\n"
            f"1. Read dailyplan_id={DAILYPLAN_ID}.\n"
            "2. Compare it against these targets:\n"
            '   targets = {"protein": 190, "total_kcal": 2800}\n'
            '   tolerances = {"protein": 10, "total_kcal": 100}\n'
            "3. When calling compare_dailyplan_to_targets, the payload must be exactly shaped like:\n"
            '   {"dailyplan_id": DAILYPLAN_ID, "targets": {"protein": 190, "total_kcal": 2800}, "tolerances": {"protein": 10, "total_kcal": 100}}\n'
            "4. Create exactly one validated dailyplan proposal using create_validated_dailyplan_proposal.\n"
            "5. Do not try to apply changes. Do not call any apply tool. The proposal must remain pending_review.\n"
            "6. Use this proposal title: OpenAI remote MCP - Ajuste nutricional seguro.\n"
            "7. Use a summary in Spanish explaining that this proposal was generated through OpenAI remote MCP and requires human review.\n"
            "8. The create_validated_dailyplan_proposal payload must include:\n"
            '   dailyplan_id: the real dailyplan id\n'
            '   title: "OpenAI remote MCP - Ajuste nutricional seguro"\n'
            '   summary: Spanish summary\n'
            '   targets: {"protein": 190, "total_kcal": 2800}\n'
            '   tolerances: {"protein": 10, "total_kcal": 100}\n'
            '   proposed_payload: an object with intent, source, analysis, and suggested_changes\n'
            "9. In proposed_payload use:\n"
            '   intent = "adjust_dailyplan_to_targets"\n'
            '   source = "openai_remote_mcp_test"\n'
            "10. After creating the proposal, list proposals and report the created proposal id if available.\n"
        ),
    )

    print(response.output_text or "[empty output_text]")
    print("\n--- Raw output items ---")
    for item in response.output:
        print(item)


if __name__ == "__main__":
    main()