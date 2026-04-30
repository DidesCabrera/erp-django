from notas.application.queries.read_boundaries import (
    get_readable_dailyplan_queryset,
    get_readable_meal_queryset,
)
from notas.domain.models import DailyPlan, Meal


def get_dailyplan_for_user(user, pk):
    """
    Compatibilidad para código web existente.

    La regla canónica de lectura vive en:
    notas.application.queries.read_boundaries.
    """
    dailyplan = (
        get_readable_dailyplan_queryset(user)
        .filter(pk=pk)
        .first()
    )

    if dailyplan:
        return dailyplan

    raise DailyPlan.DoesNotExist


def get_meal_for_user(user, meal_id):
    """
    Compatibilidad para código web existente.

    La regla canónica de lectura vive en:
    notas.application.queries.read_boundaries.
    """
    meal = (
        get_readable_meal_queryset(user)
        .filter(pk=meal_id)
        .first()
    )

    if meal:
        return meal

    raise Meal.DoesNotExist