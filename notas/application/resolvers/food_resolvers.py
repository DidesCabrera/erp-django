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
# 1. ENTITY ACTION DEFINITIONS
# ==================================================

FOOD_ENTITY_ACTION_DEFINITIONS = {
    "detail": {
        "label": "View",
        "method": "get",
        "icon": "chevron-right",
        "order": 90,
        "desktop_position": "inline",
        "mobile_position": "inline",
        "get_url": lambda food, context=None: food_url(food),
    },

    "cancel": {
        "label": "Cancel",
        "method": "get",
        "icon": "chevron-right",
        "order": 90,
        "desktop_position": "inline",
        "mobile_position": "inline",
        "get_url": lambda food, context=None: food_list_url(),
    },

    "delete": {
        "label": "Delete",
        "method": "post",
        "icon": "chevron-right",
        "order": 90,
        "desktop_position": "menu",
        "mobile_position": "menu",
        "get_url": lambda food, context=None: reverse(
            "food_delete", args=[food.id]
        ),
    },

    "edit": {
        "label": "Edit",
        "method": "post",
        "icon": "pencil",
        "order": 90,
        "desktop_position": "menu",
        "mobile_position": "menu",
        "get_url": lambda food, context=None: reverse(
            "food_edit", args=[food.id]
        ),
    },

    "save": {
        "label": "Save",
        "method": "post",
        "icon": "chevron-right",
        "order": 90,
        "desktop_position": "inline",
        "mobile_position": "inline",
        "get_url": lambda food, context=None: reverse(
            "food_detail", args=[food.id]
        ),
    },
}


# ==================================================
# 2. ENTITY ACTIONS BY VIEWMODE
# ==================================================

FOOD_ENTITY_ACTIONS_BY_VIEWMODE = {
    FOOD_VIEWMODE_PERSONAL_LIST: [
        "detail",
    ],

    FOOD_VIEWMODE_PERSONAL_DETAIL: [
        "edit",
        "delete",
    ],

    FOOD_VIEWMODE_PERSONAL_EDIT: [
        "save",
        "cancel",
    ],

    FOOD_VIEWMODE_MEAL: [
        "detail",
    ],
}


# ==================================================
# 3. PAGE ACTION DEFINITIONS
# ==================================================

FOOD_PAGE_ACTION_DEFINITIONS = {
    "create": {
        "label": "Crear",
        "method": "get",
        "icon": "plus",
        "order": 10,
        "desktop_position": "inline",
        "mobile_position": "inline",
        "get_url": lambda user, context=None: reverse("food_create"),
    },
}


# ==================================================
# 4. PAGE ACTIONS BY VIEWMODE
# ==================================================

FOOD_PAGE_ACTIONS_BY_VIEWMODE = {
    FOOD_VIEWMODE_PERSONAL_LIST: [
        "create",
    ],
}


# ==================================================
# 5. INTERNAL BUILDERS
# ==================================================

def _build_actions_from_definitions(
    *,
    definitions,
    allowed_keys,
    subject,
    caps=None,
):
    actions = []

    for key in allowed_keys:
        definition = definitions.get(key)
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
                url = get_url(subject, None)
            except TypeError:
                url = get_url(subject)

        except NoReverseMatch:
            continue

        actions.append(
            {
                "key": key,
                "label": definition["label"],
                "url": url,
                "method": definition["method"],
                "icon": definition.get("icon"),
                "order": definition.get("order", 100),
                "is_back": definition.get("is_back", False),
                "desktop_position": definition.get("desktop_position", "inline"),
                "mobile_position": definition.get("mobile_position", "inline"),
            }
        )

    return actions


# ==================================================
# 6. ENTITY RESOLVER
# ==================================================

def resolve_food_entity_actions(food, user, viewmode):
    caps = get_capabilities(user)
    allowed_keys = FOOD_ENTITY_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    return _build_actions_from_definitions(
        definitions=FOOD_ENTITY_ACTION_DEFINITIONS,
        allowed_keys=allowed_keys,
        subject=food,
        caps=caps,
    )


# ==================================================
# 7. PAGE RESOLVER
# ==================================================

def resolve_food_page_actions(user, viewmode):
    allowed_keys = FOOD_PAGE_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    return _build_actions_from_definitions(
        definitions=FOOD_PAGE_ACTION_DEFINITIONS,
        allowed_keys=allowed_keys,
        subject=user,
        caps=None,
    )


# ==================================================
# 8. COMPATIBILITY ALIAS
# ==================================================

def resolve_food_actions(food, user, viewmode):
    return resolve_food_entity_actions(food, user, viewmode)