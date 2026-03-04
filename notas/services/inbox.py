from dataclasses import dataclass
from datetime import datetime
from django.urls import reverse
from notas.models import DailyPlanShare, MealShare

# ----------------------------
# CONTRATO
# ----------------------------

@dataclass
class InboxItem:
    kind: str               # "dailyplan" | "meal"
    created_at: datetime
    sender: str
    title: str
    open_url: str
    dismiss_url: str


# ----------------------------
# BUILDER
# ----------------------------


def build_inbox_items(user):

    items = []

    # ----------------------------
    # DailyPlan Shares
    # ----------------------------
    shares_dp = DailyPlanShare.objects.filter(
        accepted_by=user,
        dismissed=False,
    ).select_related("dailyplan", "sender")

    for share in shares_dp:
        items.append(
            InboxItem(
                kind="dailyplan",
                created_at=share.created_at,
                sender=share.sender.username,
                title=share.dailyplan.name,
                open_url=reverse(
                    "dailyplan_shared_detail",
                    args=[share.dailyplan.id]
                ),
                dismiss_url=reverse(
                    "dailyplan_share_dismiss",
                    args=[share.id]
                )
            )
        )

    # ----------------------------
    # Meal Shares
    # ----------------------------
    shares_meal = MealShare.objects.filter(
        accepted_by=user,
        dismissed=False,
    ).select_related("meal", "sender")

    for share in shares_meal:
        items.append(
            InboxItem(
                kind="meal",
                created_at=share.created_at,
                sender=share.sender.username,
                title=share.meal.name,
                open_url=reverse(
                    "meal_share_detail",
                    args=[share.meal.id]
                ),
                dismiss_url=reverse(
                    "meal_share_dismiss",
                    args=[share.id]
                )
            )
        )

    # ----------------------------
    # Orden global por fecha
    # ----------------------------
    items.sort(key=lambda x: x.created_at, reverse=True)

    return items
