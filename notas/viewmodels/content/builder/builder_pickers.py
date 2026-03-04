"""
    Construyen el estado inicial de Pickers.
    - mealfood = None  → ADD
    - mealfood != None → EDIT
"""

def build_food_picker_context(*, meal, nutrition_kpis, mealfood=None):
    
    base = {
        "meal": {
            "id": meal.id,
            "kpis": nutrition_kpis,
        },
    }

    if mealfood:
        return {
            **base,
            "mode": "edit",
            "editing": {
                "mealfood_id": mealfood.id,
                "food_id": mealfood.food_id,
                "original_quantity": float(mealfood.quantity),
            },
        }

    return {
        **base,
        "mode": "add",
        "editing": None,
    }


def build_dpm_food_picker_context(
    *,
    meal,
    nutrition_kpis,
    dailyplan,
    dp_nutrition_kpis,
    mealfood=None,
):
    context = {
        "meal": {
            "id": meal.id,
            "kpis": nutrition_kpis,
        },
        "dailyplan": {
            "id": dailyplan.id,
            "kpis": dp_nutrition_kpis,
        },
        "mode": "add",
        "editing": None,
    }

    if mealfood:
        context["mode"] = "edit"
        context["editing"] = {
            "mealfood_id": mealfood.id,
            "food_id": mealfood.food_id,
            "original_quantity": float(mealfood.quantity),
        }

    return context


def build_meal_picker_context(*, dailyplan, nutrition_kpis, dailyplanmeal=None):

    base = {
        "dailyplan": {
            "id": dailyplan.id,
            "kpis": nutrition_kpis,
        },
    }

    if dailyplanmeal:
        return {
            **base,
            "mode": "edit",
            "editing": {
                "dailyplanmeal_id": dailyplanmeal.id,
                "meal_id": dailyplanmeal.meal.id,

                # 🔹 campos propios de DailyPlanMeal (EDITABLES)
                "hour": (
                    dailyplanmeal.hour.strftime("%H:%M")
                    if dailyplanmeal.hour
                    else ""
                ),
                "note": dailyplanmeal.note or "",

                # 🔹 solo para preview (NO editable)
                "original_kpis": {
                    "total_kcal": float(dailyplanmeal.meal.total_kcal),
                    "protein": float(dailyplanmeal.meal.protein),
                    "carbs": float(dailyplanmeal.meal.carbs),
                    "fat": float(dailyplanmeal.meal.fat),
                },
            },
        }

    return {
        **base,
        "mode": "add",
        "editing": None,
    }
