from notas.domain.models import DailyPlan, DailyPlanShare

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
