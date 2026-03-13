from django.urls import reverse, NoReverseMatch

from notas.services.capabilities import get_capabilities
from notas.actions.constants import *

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# (qué es cada acción, NO cuándo aparece)
# ==================================================

DAILYPLAN_MEAL_ACTION_DEFINITIONS = {
    "detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "dailyplan_meal_detail",
            args=[dpm.dailyplan.id, dpm.id],
        ),
    },

    "replace": {
        "label": "Cambiar",
        "method": "get",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "replace_dailyplan_meal",
            args=[dpm.dailyplan.id, dpm.id],
        ),
        # capability futura (safe no-op hoy)
        "capability": "can_edit_own_content",
    },

    "remove": {
        "label": "Quitar",
        "method": "post",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "remove_meal",
            args=[dpm.dailyplan.id, dpm.id],
        ),
        "capability": "can_edit_own_content",
    },

    "back_dp_detail": {
        "label": "Volver",
        "method": "get",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "dailyplan_detail",
            args=[dpm.dailyplan.id],
        ),
    },

    "back_dpm_detail": {
        "label": "Finalizar",
        "method": "get",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "dailyplan_meal_detail",
            args=[dpm.dailyplan.id, dpm.id],
        ),
    },

    "deep_edit": {
        "label": "Editar Alimentos",
        "method": "get",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "dailyplanmeal_deepedit",
            args=[dpm.dailyplan.id, dpm.id],
        ),
    },
}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

DAILYPLAN_MEAL_ACTIONS_BY_VIEWMODE = {
    # Card dentro del DailyPlan
    DAILYPLAN_MEAL_VIEWMODE_LIST: [
        "detail",
        "replace",
    ],

    # Vista detail del DailyPlanMeal
    DAILYPLAN_MEAL_VIEWMODE_DETAIL: [
        "replace",
        "deep_edit",
        "remove",
        "back_dp_detail",
    ],

    DAILYPLAN_MEAL_VIEWMODE_PERSONAL_DEEP_EDIT:[
        "back_dpm_detail",
    ],

    DAILYPLAN_MEAL_VIEWMODE_DRAFT_DEEP_EDIT:[
        "back_dpm_detail",
    ],

    DAILYPLAN_VIEWMODE_PERSONAL_DETAIL: [
        "detail",
        "deep_edit",
        "remove",
    ],

    DAILYPLAN_VIEWMODE_EXPLORE_DETAIL: [],
    DAILYPLAN_VIEWMODE_SHARED_DETAIL: [],
    DAILYPLAN_VIEWMODE_DRAFT_DETAIL: [
        "deep_edit",
        "remove",
    ],
    DAILYPLAN_VIEWMODE_PERSONAL_EDIT: [
        "deep_edit",
        "remove",
    ],
}


# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_dailyplan_meal_actions(dpm, user, context=None):
    """
    Devuelve las acciones disponibles para un DailyPlanMeal,
    según contexto + capabilities del usuario.
    """

    context = context or {}
    context_name = context.get("name")

    caps = get_capabilities(user)
    actions = []

    allowed_keys = DAILYPLAN_MEAL_ACTIONS_BY_VIEWMODE.get(context_name, [])

    for key in allowed_keys:
        definition = DAILYPLAN_MEAL_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        # --- capability check ---
        capability_name = definition.get("capability")
        if capability_name:
            if not caps or not hasattr(caps, capability_name):
                continue
            if not getattr(caps, capability_name)():
                continue

        # --- resolver URL (safe) ---
        try:
            url = definition["get_url"](dpm, context)
        except NoReverseMatch:
            continue

        actions.append({
            "key": key,
            "label": definition["label"],
            "url": url,
            "method": definition["method"],
            "group": definition.get("group", "primary"),
            "icon": definition.get("icon"),
            "order": definition.get("order", 100),
        })

    return actions
