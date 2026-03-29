from django.urls import reverse, NoReverseMatch
from notas.presentation.config.viewmodel_config import *

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# ==================================================

SHARE_ACTION_DEFINITIONS = {
    "unshare_dailyplan": {
        "label": "Quitar",
        "method": "post",
        "get_url": lambda share, context=None: reverse(
            "dailyplan_unshare", args=[share.id]
        ),
    },
    
    "unshare_meal": {
        "label": "Quitar",
        "method": "post",
        "get_url": lambda share, ctx=None: reverse(
            "meal_unshare", args=[share.id]
        ),
    },
}


# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

SHARE_ACTIONS_BY_VIEWMODE = {
    DAILYPLAN_VIEWMODE_SHARED_LIST: [
        "unshare_dailyplan",
    ],

    MEAL_VIEWMODE_SHARED_LIST: [
        "unshare_meal",
    ],
}

# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_share_actions(share, user, context=None):
    """
    Devuelve acciones disponibles para una relación DailyPlanShare
    """

    context = context or {}
    context_name = context.get("name")

    actions = []
    allowed_keys = SHARE_ACTIONS_BY_VIEWMODE.get(context_name, [])

    for key in allowed_keys:
        definition = SHARE_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        try:
            url = definition["get_url"](share, context)
        except NoReverseMatch:
            continue

        actions.append({
            "key": key,
            "label": definition["label"],
            "url": url,
            "method": definition["method"],
        })

    return actions
