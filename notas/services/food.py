# notas/services/food.py

from notas.models import Food


def create_food(user, name, protein, carbs, fat):
    food = Food.objects.create(
        name=name,
        protein=protein,
        carbs=carbs,
        fat=fat,
        created_by=user
    )

    return food