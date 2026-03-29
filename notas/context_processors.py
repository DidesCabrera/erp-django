from notas.application.services.weight import get_current_weight
from notas.domain.models import DailyPlanShare

def user_weight(request):
    if request.user.is_authenticated:
        return {"current_weight": get_current_weight(request.user)}
    return {"current_weight": None}

def shared_count(request):
    if request.user.is_authenticated:
        return {
            "shared_count": DailyPlanShare.objects.filter(
                accepted_by=request.user,
                dismissed=False
            ).count()
        }
    return {}
