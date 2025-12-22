from django.urls import reverse, NoReverseMatch
from notas.services.permissions import (
    can_fork,
    can_copy,
)
from notas.routing.meal import meal_url
from notas.actions.constants import (
    MEAL_CONTEXT_LIST,
    MEAL_CONTEXT_DAILYPLAN,
)

MEAL_ACTIONS_BY_CONTEXT = {
    MEAL_CONTEXT_LIST: [
        "detail",
        "fork",
        "copy",
    ],
    MEAL_CONTEXT_DAILYPLAN: [
        "detail",
        "replace",
        "remove",
    ],
}


# --------------------------------------------------
# Declaración de acciones posibles (no ejecuta lógica)
# --------------------------------------------------

MEAL_ACTION_DEFINITIONS = {
    "detail": {
        "label": "View",
        "method": "get",
        "get_url": lambda meal, context=None: meal_url(
            meal,
            dailyplan=context.get("dailyplan") if context else None,
        ),
    },

    "fork": {
        "label": "Fork",
        "method": "post",
        "get_url": lambda meal: reverse("fork_meal", args=[meal.id]),
        "permission": lambda meal, user: can_fork(user.profile),
    },

    "copy": {
        "label": "Copy",
        "method": "post",
        "get_url": lambda meal: reverse("copy_meal", args=[meal.id]),
        "permission": lambda meal, user: can_copy(user.profile),
    },

    # -------- FUTURAS (safe: no rompen) --------

    "add_to_dailyplan": {
        "label": "Add to plan",
        "method": "post",
        "get_url": lambda meal: reverse(
            "add_meal_to_dailyplan_from_meal",
            args=[meal.id],
        ),
    },

    "replace": {
        "label": "Replace",
        "method": "post",
        "get_url": lambda meal: reverse("replace_meal", args=[meal.id]),
    },

    "edit": {
        "label": "Edit",
        "method": "get",
        "get_url": lambda meal: reverse("meal_edit", args=[meal.id]),
    },

    "delete": {
        "label": "Delete",
        "method": "post",
        "get_url": lambda meal: reverse("meal_delete", args=[meal.id]),
    },
}


def resolve_meal_actions(meal, user, context=None):
    """
    Returns a list of resolved actions for a Meal instance.
    - Respects meal.available_action_keys()
    - Checks permissions if defined
    - Skips actions whose URLs are not implemented yet
    """
    context = context or {}
    actions = []

    context_name = context.get("context")

    allowed_keys = MEAL_ACTIONS_BY_CONTEXT.get(
        context_name,
        meal.available_action_keys(),  # fallback seguro
    )

    for key in allowed_keys:
        definition = MEAL_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        # Permiso (si existe)
        permission = definition.get("permission")
        if permission and not permission(meal, user):
            continue

        # URL segura (puede no existir aún)
        try:
            url = definition["get_url"](meal)
        except NoReverseMatch:
            continue

        actions.append({
            "key": key,
            "label": definition["label"],
            "url": url,
            "method": definition.get("method", "get"),
        })

    return actions
