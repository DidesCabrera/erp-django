from django.urls import reverse, NoReverseMatch

from notas.application.services.access.capabilities import get_capabilities
from notas.presentation.config.viewmodel_config import *

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# (qué es cada acción, NO cuándo aparece)
# ==================================================

DAILYPLAN_MEAL_ACTION_DEFINITIONS = {
    "detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
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
        "icon": "repeat",
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
        "icon": "chevron-left",
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
        "icon": "check",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "dailyplan_meal_detail",
            args=[dpm.dailyplan.id, dpm.id],
        ),
    },

    "edit": {
        "label": "Editar",
        "method": "get",
        "group": "primary",
        "icon": "settings-2",
        "order": 90,
        "get_url": lambda dpm, context=None: reverse(
            "dailyplan_meal_edit",
            args=[dpm.dailyplan.id, dpm.id],
        ),
        "capability": "can_edit_own_content",
    },
}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

DAILYPLAN_MEAL_ACTIONS_BY_VIEWMODE = {
    # Card dentro del DailyPlan
    DAILYPLAN_MEAL_VIEWMODE_LIST: [
        "replace",
        "detail",
    ],

    # Vista detail del DailyPlanMeal
    DAILYPLAN_MEAL_VIEWMODE_DETAIL: [
        "back_dp_detail",
        "replace",
        "edit",
        "remove",
    ],


    DAILYPLAN_MEAL_VIEWMODE_DRAFT_DEEP_EDIT:[
        "back_dpm_detail",
    ],
    
    # ===============================
    # ===== DAILYPLAN VIEWMODE ======
    # ===============================

    DAILYPLAN_VIEWMODE_PERSONAL_DETAIL: [
        "remove",
        "detail",
    ],

    DAILYPLAN_VIEWMODE_EXPLORE_DETAIL: [],
    DAILYPLAN_VIEWMODE_SHARED_DETAIL: [],
    DAILYPLAN_VIEWMODE_DRAFT_DETAIL: [
        "remove",
    ]
}


# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_dailyplan_meal_actions(dpm, user, viewmode):
    """
    Devuelve una lista de acciones disponibles para un DailyPlanMeal,
    según viewmode + capabilities del usuario.
    """

    caps = get_capabilities(user)
    actions = []

    allowed_keys = DAILYPLAN_MEAL_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    for key in allowed_keys:
        definition = DAILYPLAN_MEAL_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        capability_name = definition.get("capability")
        if capability_name:
            if not caps or not hasattr(caps, capability_name):
                continue
            if not getattr(caps, capability_name)():
                continue

        try:
            get_url = definition["get_url"]

            try:
                url = get_url(dpm, None)
            except TypeError:
                url = get_url(dpm)

        except NoReverseMatch:
            continue

        actions.append(
            {
                "key": key,
                "label": definition["label"],
                "url": url,
                "method": definition["method"],
                "group": definition.get("group", "primary"),
                "icon": definition.get("icon"),
                "order": definition.get("order", 100),
                "is_back": definition.get("is_back", False),
            }
        )

    return actions