from django.urls import reverse
from notas.services.permissions import can_fork, can_copy


def resolve_dailyplan_actions(dailyplan, user):
    actions = []

    actions.append({
        "key": "detail",
        "label": "View",
        "url": dailyplan.get_absolute_url(),
    })

    actions.append({
        "key": "configure",
        "label": "Configure",
        "url": dailyplan.get_configure_url(),
    })

    if can_fork(user.profile) and dailyplan.is_forkable:
        actions.append({
            "key": "fork",
            "label": "Fork",
            "url": reverse("fork_dailyplan", args=[dailyplan.id]),
        })

    if can_copy(user.profile) and dailyplan.is_copiable:
        actions.append({
            "key": "copy",
            "label": "Copy",
            "url": reverse("copy_dailyplan", args=[dailyplan.id]),
        })

    return actions
