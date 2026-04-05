from notas.presentation.viewmodels.content.kpi_contract import KPIContract
from notas.application.services.nutrition.nutrition_kpis import get_ppk_dailyplan, get_ppk_meal




def kpis_from_dailyplan_LEGACY(dp, user):
    raw = get_ppk_dailyplan(dp, user)
    return KPIContract(raw, ppk=raw.get("ppk"))


def kpis_from_meal_LEGACY(meal, user):
    raw = get_ppk_meal(meal, user)
    return KPIContract(raw, ppk=raw.get("ppk"))