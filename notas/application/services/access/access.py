from django.shortcuts import get_object_or_404

from notas.domain.models import (
    DailyPlan,
    DailyPlanShare,
    Meal,
    MealShare,
)

def get_dailyplan_for_user(user, pk):
    """
    Permite acceder a un dailyplan si:
    - es del usuario
    - es público
    - fue compartido con él
    """

    # 1️⃣ Es mío
    try:
        return DailyPlan.objects.get(pk=pk, created_by=user)
    except DailyPlan.DoesNotExist:
        pass

    # 2️⃣ Es público
    try:
        return DailyPlan.objects.get(pk=pk, is_public=True)
    except DailyPlan.DoesNotExist:
        pass

    # 3️⃣ Fue compartido conmigo
    share = DailyPlanShare.objects.filter(
        dailyplan_id=pk,
        accepted_by=user,
        dismissed=False
    ).select_related("dailyplan").first()

    if share:
        return share.dailyplan

    raise DailyPlan.DoesNotExist



def get_meal_for_user(user, meal_id):
    """
    Permite acceder a una meal si:
    - es del usuario
    - es pública
    - fue compartida con él
    """

    # 1. Es mía
    try:
        return Meal.objects.get(
            pk=meal_id,
            created_by=user,
        )
    except Meal.DoesNotExist:
        pass

    # 2. Es pública y visible en Explore
    try:
        return Meal.objects.get(
            pk=meal_id,
            is_public=True,
            is_draft=False,
        )
    except Meal.DoesNotExist:
        pass

    # 3. Fue compartida conmigo
    share = (
        MealShare.objects
        .filter(
            meal_id=meal_id,
            accepted_by=user,
            dismissed=False,
            removed=False,
        )
        .select_related("meal")
        .first()
    )

    if share:
        return share.meal

    raise Meal.DoesNotExist