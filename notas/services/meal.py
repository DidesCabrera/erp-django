# notas/services/meal.py
from django.db import transaction
from notas.models import Meal, MealFood

# ==================================================
# MEAL HELPERS
# ==================================================

def get_meal_origin(meal: Meal) -> Meal:
    """
    Retorna la Meal raíz.
    Si meal es un fork → devuelve su original root.
    """
    return meal.forked_from or meal


def clone_meal_foods(source: Meal, target: Meal) -> None:
    """
    Snapshot completo de foods desde source hacia target.
    """
    MealFood.objects.bulk_create([
        MealFood(
            meal=target,
            food=mf.food,
            quantity=mf.quantity
        )
        for mf in source.meal_food_set.all()
    ])


# ==================================================
# MEAL ACTIONS
# ==================================================

@transaction.atomic
def fork_meal(original: Meal, user) -> Meal:
    """
    Fork tipo GitHub:

    - forked_from apunta siempre al root
    - original_author siempre es el creador original
    - snapshot foods
    """

    origin = get_meal_origin(original)

    forked = Meal.objects.create(
        name=f"{original.name} (fork)",
        created_by=user,

        forked_from=origin,
        original_author=origin.created_by,

        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    clone_meal_foods(original, forked)

    return forked


@transaction.atomic
def copy_meal(original: Meal, user) -> Meal:
    """
    Copy limpio:

    - sin trazabilidad
    - forked_from=None
    - original_author=None
    """

    copy = Meal.objects.create(
        name=f"{original.name} (copy)",
        created_by=user,

        forked_from=None,
        original_author=None,

        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    clone_meal_foods(original, copy)

    return copy


def save_meal(original: Meal, user) -> Meal:
    """
    Explore UX: Guardar = Fork
    """
    return fork_meal(original, user)
