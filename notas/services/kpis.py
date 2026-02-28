from notas.services.weight import get_current_weight
from notas.viewmodels.kpi_contract import KPIContract


#=====CALCULO PPK=========

def get_ppk_meal(meal, user):
    weight = get_current_weight(user)
    ppk = (meal.protein / weight) if (weight and meal.protein) else None
    return {
        "ppk": ppk,
    }

def get_ppk_dailyplan(dailyplan, user): 
    weight = get_current_weight(user)
    ppk = (dailyplan.protein / weight) if (weight and dailyplan.protein) else None
    return {
        "ppk": ppk,
    }



#=====TRAIDOS DESDE NUTRITION=========

def build_nutrition_kpis_from_meal(meal, user):
    return {
        "total_kcal": float(meal.total_kcal),

        "protein": float(meal.protein),
        "carbs": float(meal.carbs),
        "fat": float(meal.fat),

        "alloc": {
            "protein": float(meal.alloc["protein"]),
            "carbs": float(meal.alloc["carbs"]),
            "fat": float(meal.alloc["fat"]),
        },

        "ppk": get_ppk_meal(meal, user),
        "weight": get_current_weight (user)
    }



def build_nutrition_kpis_from_dailyplan(dailyplan, user):
    return {
        "total_kcal": float(dailyplan.total_kcal),
        
        "protein": float(dailyplan.protein),
        "carbs": float(dailyplan.carbs),
        "fat": float(dailyplan.fat),

        "alloc": {
            "protein": float(dailyplan.alloc["protein"]),
            "carbs": float(dailyplan.alloc["carbs"]),
            "fat": float(dailyplan.alloc["fat"]),
        },

        "ppk": get_ppk_dailyplan(dailyplan, user),
        "weight": get_current_weight (user)
    }


#=====REFACTO VIEW MODELS=========

def kpis_from_dailyplan(dp, user):
    raw = get_ppk_dailyplan(dp, user)
    return KPIContract(raw, ppk=raw.get("ppk"))


def kpis_from_meal(meal, user):
    raw = get_ppk_meal(meal, user)
    return KPIContract(raw, ppk=raw.get("ppk"))
