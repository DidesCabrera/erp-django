from django.urls import reverse
from notas.jscontext.food_picker import FoodPickerLegacyContext, FoodPickerFoodsPayload


def build_food_picker_context_payload(
    *,
    meal,
    nutrition_kpis,
    mealfood,
):
    base = {
        "meal": {
            "id": meal.id,
            "kpis": nutrition_kpis,
        }
    }

    if mealfood:
        return FoodPickerLegacyContext(
            **base,
            mode="edit",
            editing={
                "mealfood_id": mealfood.id,
                "food_id": mealfood.food_id,
                "original_quantity": float(mealfood.quantity),
            }
        )

    return FoodPickerLegacyContext(
        **base,
        mode="add",
        editing=None,
    )

def build_food_picker_foods_payload(foods_qs):
    return FoodPickerFoodsPayload(
        foods=[
            {
                "id": f.id,
                "name": f.name,
                "total_kcal": float(f.total_kcal),
                "protein": float(f.protein),
                "carbs": float(f.carbs),
                "fat": float(f.fat),
                "alloc": {
                    "protein": float(f.alloc["protein"]),
                    "carbs": float(f.alloc["carbs"]),
                    "fat": float(f.alloc["fat"]),
                },
            }
            for f in foods_qs
        ]
    )
