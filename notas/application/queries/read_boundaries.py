from django.db.models import Q
from django.shortcuts import get_object_or_404

from notas.domain.models import (
    DailyPlan,
    DailyPlanShare,
    Food,
    Meal,
    MealShare,
)


def get_owned_food_queryset(user):
    return (
        Food.objects
        .filter(created_by=user)
        .order_by("name", "id")
    )


def get_readable_food_queryset(user):
    """
    Foods legibles para el usuario:
    - alimentos propios;
    - alimentos globales;
    - alimentos legacy de sistema, creados sin usuario.

    Regla de negocio:
    - is_global=True => disponible para todos;
    - created_by=user => disponible solo para ese usuario;
    - created_by=None => tratado como system/legacy global.
    """
    return (
        Food.objects
        .filter(
            Q(created_by=user)
            | Q(is_global=True)
            | Q(created_by__isnull=True)
        )
        .distinct()
        .order_by("name", "id")
    )



def get_readable_food_or_404(user, food_id: int):
    return get_object_or_404(
        get_readable_food_queryset(user),
        pk=food_id,
    )


def get_owned_meal_queryset(user):
    return (
        Meal.objects
        .filter(created_by=user)
        .order_by("name", "id")
    )


def get_readable_meal_queryset(user):
    """
    Meals legibles para el usuario:
    - propias;
    - públicas y no draft;
    - compartidas aceptadas, no dismissed y no removed.
    """
    shared_meal_ids = (
        MealShare.objects
        .filter(
            accepted_by=user,
            dismissed=False,
            removed=False,
        )
        .values_list("meal_id", flat=True)
    )

    return (
        Meal.objects
        .filter(
            Q(created_by=user)
            | Q(is_public=True, is_draft=False)
            | Q(id__in=shared_meal_ids)
        )
        .distinct()
        .order_by("name", "id")
    )


def get_readable_meal_or_404(user, meal_id: int):
    return get_object_or_404(
        get_readable_meal_queryset(user),
        pk=meal_id,
    )


def get_owned_dailyplan_queryset(user):
    return (
        DailyPlan.objects
        .filter(created_by=user)
        .order_by("name", "id")
    )


def get_readable_dailyplan_queryset(user):
    """
    DailyPlans legibles para el usuario:
    - propios;
    - públicos y no draft;
    - compartidos aceptados, no dismissed y no removed.
    """
    shared_dailyplan_ids = (
        DailyPlanShare.objects
        .filter(
            accepted_by=user,
            dismissed=False,
            removed=False,
        )
        .values_list("dailyplan_id", flat=True)
    )

    return (
        DailyPlan.objects
        .filter(
            Q(created_by=user)
            | Q(is_public=True, is_draft=False)
            | Q(id__in=shared_dailyplan_ids)
        )
        .distinct()
        .order_by("name", "id")
    )


def get_readable_dailyplan_or_404(user, dailyplan_id: int):
    return get_object_or_404(
        get_readable_dailyplan_queryset(user),
        pk=dailyplan_id,
    )