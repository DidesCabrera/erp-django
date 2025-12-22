# notas/actions/resolvers.py
from django.urls import reverse
from notas.services.permissions import can_fork, can_copy
from notas.actions.meal_resolvers import MEAL_ACTION_DEFINITIONS

def resolve_meal_actions(meal, user, context=None):
    context = context or {}
    actions = []

    for key in meal.available_action_keys():
        definition = MEAL_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        permission = definition.get("permission")
        if permission and not permission(meal, user):
            continue

        try:
            url = definition["get_url"](meal, context)
        except Exception:
            continue

        actions.append({
            "key": key,
            "label": definition["label"],
            "url": url,
            "method": definition.get("method", "get"),
        })

    return actions
