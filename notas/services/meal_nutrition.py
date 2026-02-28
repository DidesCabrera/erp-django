# notas/services/meal_nutrition.py

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


