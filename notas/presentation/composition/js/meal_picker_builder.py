from django.urls import reverse
from notas.presentation.frontend.jscontext.meal_picker import MealPickerContext, MealPickerMealsPayload


def build_meal_picker_context_payload(
    *,
    dailyplan,
    dailyplan_kpis,
    dpm,
):
    base = {
        "dailyplan": {
            "id": dailyplan.id,
            "kpis": dailyplan_kpis,
        }
    }

    if dpm:
        if dpm:
            return MealPickerContext(
                **base,
                mode="edit",
                editing={
                    "dailyplanmeal_id": dpm.id,
                    "hour": dpm.hour,
                    "note": dpm.note,

                    "original_kpis": {
                        "protein": dpm.meal.protein_cached,
                        "carbs": dpm.meal.carbs_cached,
                        "fat": dpm.meal.fat_cached,
                        "total_kcal": dpm.meal.total_kcal_cached,
                    }
                }
            )


    return MealPickerContext(
        **base,
        mode="add",
        editing=None,
    )


def build_meal_picker_meals_payload(meals_qs):
    return MealPickerMealsPayload(
        meals=[
            {
                "id": m.id,
                "name": m.name,

                "total_kcal": m.total_kcal_cached,
                "protein": m.protein_cached,
                "carbs": m.carbs_cached,
                "fat": m.fat_cached,

                "alloc": {
                    "protein": m.alloc_protein_cached,
                    "carbs": m.alloc_carbs_cached,
                    "fat": m.alloc_fat_cached,
                },

                "foods": m.foods_aggregation_cached,
            }
            for m in meals_qs
        ]
    )


def serialize_meal(m):
    return {
        "id": m.id,
        "name": m.name,
        "total_kcal": m.total_kcal_cached,
        "protein": m.protein_cached,
        "carbs": m.carbs_cached,
        "fat": m.fat_cached,
        "alloc": {
            "protein": m.alloc_protein_cached,
            "carbs": m.alloc_carbs_cached,
            "fat": m.alloc_fat_cached,
        },
        "foods": m.foods_aggregation_cached,
    }


def build_meal_picker_data_payload(*, browse_meals_qs, existing_meals_qs):
    return {
        "browse_meals": [serialize_meal(m) for m in browse_meals_qs],
        "existing_meals": [serialize_meal(m) for m in existing_meals_qs],
    }