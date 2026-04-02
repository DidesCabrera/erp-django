from notas.presentation.composition.viewmodel.components.builder_foods_aggregation import build_meal_foods_aggregation

def build_meal_foods_projection(meal):

    foods = build_meal_foods_aggregation(meal)

    ordered = sorted(
        foods,
        key=lambda x: (-x["total_grams"], x["food"].name)
    )

    return [
        {
            "id": f["food"].id,
            "name": f["food"].name,
            "grams": round(f["total_grams"], 1),
        }
        for f in ordered
    ]

