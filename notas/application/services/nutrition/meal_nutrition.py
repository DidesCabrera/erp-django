from notas.presentation.composition.viewmodel.components.builder_foods_aggregation import build_meal_foods_projection


def compute_meal_nutrition(meal):
    protein = carbs = fat = 0.0
    kcal_protein = kcal_carbs = kcal_fat = 0.0

    for mf in meal.meal_food_set.all():
        protein += mf.protein
        carbs += mf.carbs
        fat += mf.fat

        kcal_protein += mf.kcal_protein
        kcal_carbs += mf.kcal_carbs
        kcal_fat += mf.kcal_fat

    total_kcal = kcal_protein + kcal_carbs + kcal_fat

    if total_kcal > 0:
        alloc = {
            "protein": kcal_protein / total_kcal * 100,
            "carbs": kcal_carbs / total_kcal * 100,
            "fat": kcal_fat / total_kcal * 100,
        }
    else:
        alloc = {"protein": 0, "carbs": 0, "fat": 0}

    return {
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "kcal_protein": kcal_protein,
        "kcal_carbs": kcal_carbs,
        "kcal_fat": kcal_fat,
        "total_kcal": total_kcal,
        "alloc": alloc,
    }


def rebuild_meal_cached_state(meal):
    data = compute_meal_nutrition(meal)

    meal.protein_cached = data["protein"]
    meal.carbs_cached = data["carbs"]
    meal.fat_cached = data["fat"]

    meal.kcal_protein_cached = data["kcal_protein"]
    meal.kcal_carbs_cached = data["kcal_carbs"]
    meal.kcal_fat_cached = data["kcal_fat"]
    meal.total_kcal_cached = data["total_kcal"]

    meal.alloc_protein_cached = data["alloc"]["protein"]
    meal.alloc_carbs_cached = data["alloc"]["carbs"]
    meal.alloc_fat_cached = data["alloc"]["fat"]

    meal.foods_aggregation_cached = build_meal_foods_projection(meal)

    meal.save(
        update_fields=[
            "protein_cached",
            "carbs_cached",
            "fat_cached",
            "kcal_protein_cached",
            "kcal_carbs_cached",
            "kcal_fat_cached",
            "total_kcal_cached",
            "alloc_protein_cached",
            "alloc_carbs_cached",
            "alloc_fat_cached",
            "foods_aggregation_cached",
        ]
    )


