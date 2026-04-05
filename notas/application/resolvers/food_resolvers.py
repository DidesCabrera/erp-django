from django.urls import reverse, NoReverseMatch
from notas.application.services.access.capabilities import get_capabilities
from notas.interface.routing.food import food_url, food_list_url
from notas.presentation.config.viewmodel_config import (
    FOOD_VIEWMODE_PERSONAL_LIST,
    FOOD_VIEWMODE_PERSONAL_DETAIL,
    FOOD_VIEWMODE_MEAL,
    FOOD_VIEWMODE_PERSONAL_EDIT,
)

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# (qué es cada acción, NO cuándo aparece)
# ==================================================

FOOD_ACTION_DEFINITIONS = {
    "detail": {
        "label": "View",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: food_url(food),
    },

    "cancel": {
        "label": "Cancel",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: food_list_url(),
    },

    # ---- FUTURAS (safe no-op si no se usan) ----

    "delete": {
        "label": "Delete",
        "method": "post",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: reverse(
            "food_delete", args=[food.id]
        ),
    },

    "edit": {
        "label": "Edit",
        "method": "post",
        "group": "primary",
        "icon": "pencil",
        "order": 90,
        "get_url": lambda food, context=None: reverse(
            "food_edit", args=[food.id]
        ),
    },

    "save": {
        "label": "Save",
        "method": "post",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: reverse(
            "food_detail", args=[food.id]
        ),
    },
}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

FOOD_ACTIONS_BY_VIEWMODE = {
    FOOD_VIEWMODE_PERSONAL_LIST: [
        "detail",
        "fork",
        "copy",
        "add_to_dailyplan",
    ],

    FOOD_VIEWMODE_PERSONAL_DETAIL: [
        "fork",
        "copy",
        "add_to_dailyplan",
        "edit",
        "delete",
    ],

    FOOD_VIEWMODE_PERSONAL_EDIT: [
        "save",
        "cancel",
    ],

    FOOD_VIEWMODE_MEAL: [
        # dentro de un dailyplan
        "detail",
    ],
}

# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_food_actions(food, user, viewmode):

    caps = get_capabilities(user)
    actions = []

    # --- acciones permitidas según contexto ---
    allowed_keys = FOOD_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    for key in allowed_keys:
        definition = FOOD_ACTION_DEFINITIONS.get(key)
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
            get_url = definition["get_url"]
            try:
                url = get_url(food, None)
            except TypeError:
                url = get_url(food)
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
