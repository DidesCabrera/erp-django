from notas.domain.models import WeightLog

def get_current_weight(user):
    last = user.weight_logs.first()
    return last.weight_kg if last else None
