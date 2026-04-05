from django.urls import NoReverseMatch, reverse

from notas.application.services.access.capabilities import get_capabilities
from notas.interface.routing.food import food_list_url, food_url
from notas.presentation.config.viewmodel_config import (
    MEAL_FOOD_VIEWMODE_DETAIL,
    MEAL_FOOD_VIEWMODE_DRAFT_DEEP_EDIT,
    MEAL_FOOD_VIEWMODE_LIST,
    MEAL_FOOD_VIEWMODE_PERSONAL_DEEP_EDIT,
)


# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# (qué es cada acción, NO cuándo aparece)
# ==================================================

MEAL_FOOD_ACTION_DEFINITIONS = {
    "detail": {
        "label": "View",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food: food_url(food),
    },
    "cancel": {
        "label": "Cancel",
        "method": "get",
        "group": "primary",
        "icon": "x",
        "order": 90,
        "get_url": lambda food: food_list_url(),
    },
    "delete": {
        "label": "Delete",
        "method": "post",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda food: reverse(
            "food_delete",
            args=[food.id],
        ),
    },
    "edit": {
        "label": "Edit",
        "method": "get",
        "group": "primary",
        "icon": "pencil",
        "order": 90,
        "get_url": lambda food: reverse(
            "food_edit",
            args=[food.id],
        ),
    },
    "save": {
        "label": "Save",
        "method": "post",
        "group": "primary",
        "icon": "check",
        "order": 90,
        "get_url": lambda food: reverse(
            "food_detail",
            args=[food.id],
        ),
    },
}


# ==================================================
# 2. ACCIONES PERMITIDAS POR VIEWMODE
# ==================================================

MEAL_FOOD_ACTIONS_BY_VIEWMODE = {
    MEAL_FOOD_VIEWMODE_LIST: [
        "detail",
    ],
    MEAL_FOOD_VIEWMODE_DETAIL: [
        "detail",
        "edit",
        "delete",
    ],
    MEAL_FOOD_VIEWMODE_PERSONAL_DEEP_EDIT: [
        "save",
        "cancel",
    ],
    MEAL_FOOD_VIEWMODE_DRAFT_DEEP_EDIT: [
        "save",
        "cancel",
    ],
}


# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_meal_food_actions(food, user, viewmode):
    """
    Devuelve una lista de acciones disponibles para un food
    renderizado en el contexto meal_food, según viewmode
    + capabilities del usuario.
    """

    caps = get_capabilities(user)
    actions = []

    allowed_keys = MEAL_FOOD_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    for key in allowed_keys:
        definition = MEAL_FOOD_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        capability_name = definition.get("capability")
        if capability_name:
            if not caps or not hasattr(caps, capability_name):
                continue
            if not getattr(caps, capability_name)():
                continue

        try:
            url = definition["get_url"](food)
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