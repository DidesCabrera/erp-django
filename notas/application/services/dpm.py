from django.db import transaction
from notas.domain.models import Meal, MealFood


@transaction.atomic
def ensure_dpm_meal_isolated(dpm, user):
    """
    Garantiza que el DPM edite una Meal aislada (copy-on-write).
    Si la meal no es exclusiva para este DPM, se crea un fork y se reasigna.

    MISMA lógica que antes.
    Única mejora: forked_from apunta al root.
    """

    meal = dpm.meal

    # --- tu regla original (la respetamos) ---
    if meal.forked_from is None or meal.created_by != user:

        # ✅ FIX: root origin
        origin = meal.forked_from or meal

        fork = Meal.objects.create(
            name=f"{meal.name} (edited)",
            created_by=user,
            is_draft=True,

            forked_from=origin,
            original_author=origin.created_by,
        )

        # Copiar foods (igual que antes)
        for mf in meal.meal_food_set.all():
            MealFood.objects.create(
                meal=fork,
                food=mf.food,
                quantity=mf.quantity,
            )

        dpm.meal = fork
        dpm.save()

        return fork

    return meal
