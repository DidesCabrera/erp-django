def build_dailyplanmeal_table_item(dpm):
    dailyplan = dpm.dailyplan
    meal = dpm.meal

    # ==================================================
    # Freeze MEAL aggregates (cached if available)
    # ==================================================

    meal_total_kcal = meal.total_kcal_cached or meal.total_kcal
    meal_protein = meal.protein_cached or meal.protein
    meal_carbs = meal.carbs_cached or meal.carbs
    meal_fat = meal.fat_cached or meal.fat

    # alloc del meal relativo al dailyplan
    dpm_alloc = dpm.alloc

    return {
        # entidad principal
        "main_id": dailyplan.id,
        "child_id": meal.id,

        # RELACIÓN EXPLÍCITA
        "rel": {
            "id": dpm.id,
            "hour": dpm.hour,
            "note": dpm.note,

            "name": meal.name,

            "total_kcal": meal_total_kcal,
            "g_protein": meal_protein,
            "g_carbs": meal_carbs,
            "g_fat": meal_fat,

            "alloc_protein": dpm_alloc["protein"],
            "alloc_carbs": dpm_alloc["carbs"],
            "alloc_fat": dpm_alloc["fat"],
        },
    }





def build_mealfood_table_item(mf):
    food = mf.food

    # ==================================================
    # Freeze MF aggregates (mf ya es “materializado”)
    # ==================================================

    mf_total_kcal = mf.total_kcal
    mf_protein = mf.protein
    mf_carbs = mf.carbs
    mf_fat = mf.fat

    mf_alloc = mf.alloc

    return {
        # entidad principal
        "child": food,

        # RELACIÓN EXPLÍCITA
        "rel": {
            "id": mf.id,
            "quantity": mf.quantity,

            "name": food.name,

            "total_kcal": mf_total_kcal,
            "g_protein": mf_protein,
            "g_carbs": mf_carbs,
            "g_fat": mf_fat,

            "alloc_protein": mf_alloc["protein"],
            "alloc_carbs": mf_alloc["carbs"],
            "alloc_fat": mf_alloc["fat"],
        },
    }
