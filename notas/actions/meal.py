from django.urls import reverse, NoReverseMatch
from notas.services.permissions import can_fork, can_copy


# --------------------------------------------------
# Action definitions (declarativo, dominio)
# --------------------------------------------------

MEAL_ACTION_DEFINITIONS = {
    "detail": {
        "label": "View",
        "method": "get",
        "get_url": lambda meal: meal.get_absolute_url(),
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
    # ---- futuras (NO rompen) ----
    "add_to_dailyplan": {
        "label": "Add to plan",
        "method": "post",
        "get_url": lambda meal: reverse("add_meal_to_dailyplan_from_meal", args=[meal.id]),
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
