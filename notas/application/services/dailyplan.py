# notas/services/dailyplan.py
from django.db import transaction
from notas.domain.models import DailyPlan, DailyPlanMeal


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
    Copia todas las meals desde source hacia target (snapshot).
    """
    for dpm in source.dailyplan_meals.all():
        DailyPlanMeal.objects.create(
            dailyplan=target,
            meal=dpm.meal,
            note=dpm.note,
            hour=dpm.hour,
            order=dpm.order,
        )


# ==================================================
# DAILYPLAN ACTIONS
# ==================================================

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
