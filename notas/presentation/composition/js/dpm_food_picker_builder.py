from notas.presentation.frontend.jscontext.dpm_food_picker import DpmFoodPickerContextPayload


def build_dpm_food_picker_context_payload(
    *,
    meal,
    meal_kpis,
    dailyplan,
    dailyplan_kpis,
    mealfood=None,
):
    base = {
        "meal": {
            "id": meal.id,
            "kpis": meal_kpis,
        },
        "dailyplan": {
            "id": dailyplan.id,
            "kpis": dailyplan_kpis,
        },
    }

    if mealfood:
        return DpmFoodPickerContextPayload(
            **base,
            mode="edit",
            editing={
                "mealfood_id": mealfood.id,
                "food_id": mealfood.food_id,
                "original_quantity": float(mealfood.quantity),
            },
        )

    return DpmFoodPickerContextPayload(
        **base,
        mode="add",
        editing=None,
    )