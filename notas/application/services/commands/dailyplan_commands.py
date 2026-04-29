from dataclasses import dataclass

from django.db import transaction

from notas.domain.models import DailyPlan, DailyPlanMeal, Meal

@dataclass(frozen=True)
class DailyPlanCreateResult:
    dailyplan: DailyPlan


@dataclass(frozen=True)
class DailyPlanRenameResult:
    dailyplan: DailyPlan


@dataclass(frozen=True)
class DailyPlanDeleteResult:
    dailyplan_id: int

@dataclass(frozen=True)
class DailyPlanMealCreateResult:
    dailyplan: DailyPlan
    dailyplan_meal: DailyPlanMeal
    meal: Meal


@dataclass(frozen=True)
class DailyPlanMealDeleteResult:
    dailyplan: DailyPlan
    dailyplan_meal_id: int
    meal_id: int


# ==================================================
# DAILYPLAN HELPERS
# ==================================================

def get_dailyplan_origin(dp: DailyPlan) -> DailyPlan:
    """
    Retorna el DailyPlan raíz.

    - Si dp es un fork → devuelve el original root
    - Si dp es original → devuelve dp
    """
    return dp.forked_from or dp


def clone_dailyplan_meals(source: DailyPlan, target: DailyPlan) -> None:
    """
    Copia todas las meals desde source hacia target creando snapshots
    independientes para cada slot del DailyPlan.
    """
    from notas.application.services.commands.meal_commands import fork_meal

    for dpm in source.dailyplan_meals.all().order_by("order", "id"):
        forked_meal = fork_meal(dpm.meal, target.created_by)

        DailyPlanMeal.objects.create(
            dailyplan=target,
            meal=forked_meal,
            note=dpm.note,
            hour=dpm.hour,
            order=dpm.order,
        )


# ==================================================
# DAILYPLAN ACTIONS
# ==================================================


@transaction.atomic
def create_draft_dailyplan(
    *,
    user,
    name: str,
) -> DailyPlanCreateResult:
    clean_name = (name or "").strip()

    if not clean_name:
        raise ValueError("dailyplan_name_required")

    dailyplan = DailyPlan.objects.create(
        name=clean_name,
        created_by=user,
        is_draft=True,
    )

    return DailyPlanCreateResult(
        dailyplan=dailyplan,
    )


@transaction.atomic
def rename_dailyplan(
    *,
    dailyplan: DailyPlan,
    name: str,
) -> DailyPlanRenameResult:
    clean_name = (name or "").strip()

    if not clean_name:
        raise ValueError("dailyplan_name_required")

    dailyplan.name = clean_name
    dailyplan.save(update_fields=["name"])

    return DailyPlanRenameResult(
        dailyplan=dailyplan,
    )


@transaction.atomic
def delete_dailyplan(
    *,
    dailyplan: DailyPlan,
) -> DailyPlanDeleteResult:
    if dailyplan.is_public:
        raise ValueError("dailyplan_is_public")

    dailyplan_id = dailyplan.id
    dailyplan.delete()

    return DailyPlanDeleteResult(
        dailyplan_id=dailyplan_id,
    )


@transaction.atomic
def fork_dailyplan(original: DailyPlan, user) -> DailyPlan:
    """
    Fork tipo GitHub:
    - forked_from siempre apunta al root original
    - original_author siempre es el creador original
    - snapshot completo de meals
    """

    origin = get_dailyplan_origin(original)

    forked = DailyPlan.objects.create(
        name=f"{original.name}",
        created_by=user,

        forked_from=origin,
        original_author=origin.created_by,

        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    clone_dailyplan_meals(original, forked)

    return forked


@transaction.atomic
def copy_dailyplan(original: DailyPlan, user) -> DailyPlan:
    """
    Copy limpio:
    - NO mantiene trazabilidad
    - forked_from = None
    - original_author = None
    """

    copy = DailyPlan.objects.create(
        name=f"{original.name} (copy)",
        created_by=user,

        forked_from=None,
        original_author=None,

        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    clone_dailyplan_meals(original, copy)

    return copy


def save_dailyplan(original: DailyPlan, user) -> DailyPlan:
    """
    UX Alias:
    Explore → Guardar = Fork
    Esto permite que en resolvers/UI digas "save"
    pero internamente siempre sea fork.
    """
    return fork_dailyplan(original, user)


@transaction.atomic
def add_existing_meal_to_dailyplan(
    *,
    dailyplan: DailyPlan,
    meal: Meal,
    user,
    hour=None,
    note=None,
) -> DailyPlanMealCreateResult:
    from notas.application.services.commands.meal_commands import (
        fork_meal_for_dailyplan,
    )

    clean_note = (note or "").strip() or None

    forked_meal = fork_meal_for_dailyplan(
        meal,
        user,
    )

    next_order = dailyplan.dailyplan_meals.count() + 1

    dailyplan_meal = DailyPlanMeal.objects.create(
        dailyplan=dailyplan,
        meal=forked_meal,
        hour=hour or None,
        note=clean_note,
        order=next_order,
    )

    dailyplan.update_draft_status()

    return DailyPlanMealCreateResult(
        dailyplan=dailyplan,
        dailyplan_meal=dailyplan_meal,
        meal=forked_meal,
    )


@transaction.atomic
def remove_dailyplan_meal(
    *,
    dailyplan_meal: DailyPlanMeal,
) -> DailyPlanMealDeleteResult:
    dailyplan = dailyplan_meal.dailyplan
    meal = dailyplan_meal.meal

    dailyplan_meal_id = dailyplan_meal.id
    meal_id = meal.id

    dailyplan_meal.delete()
    meal.delete()

    return DailyPlanMealDeleteResult(
        dailyplan=dailyplan,
        dailyplan_meal_id=dailyplan_meal_id,
        meal_id=meal_id,
    )