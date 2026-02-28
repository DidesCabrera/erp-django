from collections import defaultdict

def build_dailyplan_foods_aggregation(dailyplan_meals):
    foods_aggregation = defaultdict(lambda: {
        "food": None,
        "total_grams": 0
    })

    for dpm in dailyplan_meals:
        meal = dpm.meal

        for meal_food in meal.meal_food_set.all():
            food = meal_food.food
            grams = meal_food.quantity

            foods_aggregation[food.id]["food"] = food
            foods_aggregation[food.id]["total_grams"] += grams

    return sorted(
        foods_aggregation.values(),
        key=lambda x: (-x["total_grams"], x["food"].name)
    )



def build_meal_foods_aggregation(meal):
    foods_aggregation = defaultdict(lambda: {
        "food": None,
        "total_grams": 0
    })

    for meal_food in meal.meal_food_set.all():
        food = meal_food.food
        grams = meal_food.quantity  # o .grams, según tu modelo

        foods_aggregation[food.id]["food"] = food
        foods_aggregation[food.id]["total_grams"] += grams

    return sorted(
        foods_aggregation.values(),
        key=lambda x: (-x["total_grams"], x["food"].name)
    )   

