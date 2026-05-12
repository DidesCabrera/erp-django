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
            "Create exactly one reviewable DailyPlan build proposal using foods from the My Scoope catalog.\n"
            "The proposal must represent a complete training-day diet.\n"
            "\n"
            "Hard safety rules:\n"
            "1. Call list_food_catalog first with search=null and limit=50.\n"
            "2. If list_food_catalog returns count=0, stop and do not create a proposal.\n"
            "3. Use only food_id values returned by list_food_catalog.\n"
            "4. Never use placeholder food_id values such as 0.\n"
            "5. Never use quantity <= 0.\n"
            "6. Do not invent food IDs.\n"
            "7. Do not create final DailyPlans. Only create a pending_review proposal.\n"
            "8. Do not call apply tools.\n"
            "9. Create exactly one proposal.\n"
            "\n"
            f"Associated base dailyplan_id: {DAILYPLAN_ID}\n"
            "\n"
            "Nutrition targets:\n"
            "- total_kcal: 2800\n"
            "- protein: 190\n"
            "- carbs: flexible\n"
            "- fat: flexible\n"
            "\n"
            "Requested meal structure:\n"
            "- Desayuno\n"
            "- Almuerzo\n"
            "- Intraentreno\n"
            "- Post entreno\n"
            "- Cena\n"
            "\n"
            "Preferred catalog foods if available:\n"
            "- Avena Integral\n"
            "- Leche Descremada\n"
            "- Plátano or another fruit\n"
            "- Arroz Blanco Cocido\n"
            "- Pechuga Pollo Cocida\n"
            "- Dextrosa\n"
            "- Whey Protein if available\n"
            "- Palta\n"
            "- Nueces\n"
            "- Frambuesas\n"
            "- Huevo Cocido\n"
            "\n"
            "When calling create_validated_dailyplan_build_proposal, use this exact top-level shape:\n"
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
            '              {"food_id": REAL_FOOD_ID_FROM_CATALOG, "quantity": POSITIVE_NUMBER, "unit": "g"}\n'
            '            ]\n'
            '          }\n'
            '        },\n'
            '        {\n'
            '          "hour": "13:00",\n'
            '          "note": "Almuerzo",\n'
            '          "meal": {\n'
            '            "name": "Almuerzo IA",\n'
            '            "foods": [\n'
            '              {"food_id": REAL_FOOD_ID_FROM_CATALOG, "quantity": POSITIVE_NUMBER, "unit": "g"}\n'
            '            ]\n'
            '          }\n'
            '        },\n'
            '        {\n'
            '          "hour": "16:00",\n'
            '          "note": "Intraentreno",\n'
            '          "meal": {\n'
            '            "name": "Intraentreno IA",\n'
            '            "foods": [\n'
            '              {"food_id": REAL_FOOD_ID_FROM_CATALOG, "quantity": POSITIVE_NUMBER, "unit": "g"}\n'
            '            ]\n'
            '          }\n'
            '        },\n'
            '        {\n'
            '          "hour": "18:00",\n'
            '          "note": "Post entreno",\n'
            '          "meal": {\n'
            '            "name": "Post entreno IA",\n'
            '            "foods": [\n'
            '              {"food_id": REAL_FOOD_ID_FROM_CATALOG, "quantity": POSITIVE_NUMBER, "unit": "g"}\n'
            '            ]\n'
            '          }\n'
            '        },\n'
            '        {\n'
            '          "hour": "21:00",\n'
            '          "note": "Cena",\n'
            '          "meal": {\n'
            '            "name": "Cena IA",\n'
            '            "foods": [\n'
            '              {"food_id": REAL_FOOD_ID_FROM_CATALOG, "quantity": POSITIVE_NUMBER, "unit": "g"}\n'
            '            ]\n'
            '          }\n'
            '        }\n'
            '      ]\n'
            '    },\n'
            '    "analysis": {\n'
            '      "goal": "Crear una dieta completa de entrenamiento aproximada a 2800 kcal y 190 g de proteína.",\n'
            '      "safety_boundary": "La IA solo crea una propuesta pendiente de revisión; no aplica cambios directamente.",\n'
            '      "catalog_rule": "Todos los food_id usados provienen de list_food_catalog."\n'
            '    }\n'
            '  }\n'
            "}\n"
            "\n"
            "Before calling create_validated_dailyplan_build_proposal:\n"
            "- Replace every REAL_FOOD_ID_FROM_CATALOG with an actual food_id from list_food_catalog.\n"
            "- Replace every POSITIVE_NUMBER with a positive numeric quantity.\n"
            "- Ensure no placeholders remain in proposed_payload.\n"
            "- Ensure all meals contain at least one food.\n"
            "\n"
            "After creating the proposal, call list_user_proposals and report the created proposal id if available.\n"
        ),
    )

    print(response.output_text or "[empty output_text]")
    print("\n--- Raw output items ---")
    for item in response.output:
        print(item)


if __name__ == "__main__":
    main()