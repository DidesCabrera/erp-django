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
                    "list_food_catalog",
                    "create_validated_dailyplan_build_proposal",
                    "list_user_proposals",
                    "read_proposal",
                ],
                "require_approval": "never",
            }
        ],
        input=(
            "You are an external AI connected to My Scoope through remote MCP.\n"
            "\n"
            "Goal:\n"
            "Create one reviewable DailyPlan build proposal using foods from the My Scoope catalog.\n"
            "The proposal must represent a complete training-day diet.\n"
            "\n"
            "Hard rules:\n"
            "1. Use list_food_catalog first to inspect available foods.\n"
            "2. Use only food_id values that come from list_food_catalog.\n"
            "3. Do not invent food IDs.\n"
            "4. Do not create final DailyPlans. Only create a pending_review proposal.\n"
            "5. Do not call apply tools.\n"
            "6. Create exactly one proposal.\n"
            "\n"
            f"Associated base dailyplan_id: {DAILYPLAN_ID}\n"
            "\n"
            "Nutrition targets:\n"
            "- total_kcal: 2800\n"
            "- protein: 190\n"
            "- carbs: flexible\n"
            "- fat: flexible\n"
            "\n"
            "DailyPlan structure requested:\n"
            "- Desayuno\n"
            "- Almuerzo\n"
            "- Intraentreno\n"
            "- Post entreno\n"
            "- Cena\n"
            "\n"
            "Use this exact top-level payload when calling create_validated_dailyplan_build_proposal:\n"
            "{\n"
            f'  "dailyplan_id": {DAILYPLAN_ID},\n'
            '  "title": "OpenAI remote MCP - Dieta completa de entrenamiento",\n'
            '  "summary": "Propuesta de dieta completa generada por OpenAI remote MCP usando alimentos disponibles en My Scoope. Requiere revisión humana antes de aplicarse.",\n'
            '  "targets": {"total_kcal": 2800, "protein": 190},\n'
            '  "proposed_payload": {\n'
            '    "intent": "create_dailyplan",\n'
            '    "source": "openai_remote_mcp_diet_builder_test",\n'
            '    "dailyplan": {\n'
            '      "name": "Dieta entrenamiento IA - 2800 kcal",\n'
            '      "meals": [\n'
            '        {\n'
            '          "hour": "09:00",\n'
            '          "note": "Desayuno",\n'
            '          "meal": {\n'
            '            "name": "Desayuno IA",\n'
            '            "foods": [\n'
            '              {"food_id": 0, "quantity": 0, "unit": "g"}\n'
            '            ]\n'
            '          }\n'
            '        }\n'
            '      ]\n'
            '    },\n'
            '    "analysis": {\n'
            '      "goal": "Crear una dieta completa de entrenamiento aproximada a 2800 kcal y 190 g de proteína.",\n'
            '      "safety_boundary": "La IA solo crea una propuesta pendiente de revisión; no aplica cambios directamente."\n'
            '    }\n'
            '  }\n'
            "}\n"
            "\n"
            "Important:\n"
            "- Replace the example food_id 0 and quantity 0 with real catalog food IDs and useful quantities.\n"
            "- Include multiple foods per meal when appropriate.\n"
            "- Keep units as 'g' unless the catalog clearly implies another unit.\n"
            "- After creating the proposal, list proposals and report the created proposal id.\n"
        ),
    )

    print(response.output_text or "[empty output_text]")
    print("\n--- Raw output items ---")
    for item in response.output:
        print(item)


if __name__ == "__main__":
    main()