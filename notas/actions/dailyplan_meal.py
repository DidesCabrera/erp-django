from django.urls import reverse

def resolve_dailyplan_meal_actions(item, user):
    actions = []

    if "replace_meal" in item.available_action_keys():
        actions.append({
            "key": "replace",
            "label": "Reemplazar",
            "url": reverse(
                "replace_meal",
                args=[item.daily_plan.id, item.id],
            ),
        })

    if "remove_meal" in item.available_action_keys():
        actions.append({
            "key": "remove",
            "label": "Quitar",
            "url": reverse(
                "remove_meal",
                args=[item.daily_plan.id, item.id],
            ),
        })

    return actions
