from notas.domain.models import Food

def create_food(user, name, protein, carbs, fat):
    food = Food.objects.create(
        name=name,
        protein=protein,
        carbs=carbs,
        fat=fat,
        created_by=user
    )

    return food