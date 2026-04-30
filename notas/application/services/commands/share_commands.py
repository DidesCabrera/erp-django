from dataclasses import dataclass

from django.db import transaction

from notas.domain.models import DailyPlan, DailyPlanShare, Meal, MealShare


@dataclass(frozen=True)
class DailyPlanShareCreateResult:
    share: DailyPlanShare
    created: bool


@dataclass(frozen=True)
class DailyPlanShareAcceptResult:
    share: DailyPlanShare


@dataclass(frozen=True)
class DailyPlanShareDismissResult:
    share: DailyPlanShare


@dataclass(frozen=True)
class DailyPlanShareRemoveResult:
    share: DailyPlanShare



@dataclass(frozen=True)
class MealShareCreateResult:
    share: MealShare
    created: bool


@dataclass(frozen=True)
class MealShareAcceptResult:
    share: MealShare


@dataclass(frozen=True)
class MealShareDismissResult:
    share: MealShare


@dataclass(frozen=True)
class MealShareRemoveResult:
    share: MealShare






@transaction.atomic
def create_dailyplan_share(
    *,
    sender,
    dailyplan: DailyPlan,
    recipient_email: str,
) -> DailyPlanShareCreateResult:
    clean_email = (recipient_email or "").strip().lower()

    if not clean_email:
        raise ValueError("recipient_email_required")

    share, created = DailyPlanShare.objects.get_or_create(
        sender=sender,
        recipient_email=clean_email,
        dailyplan=dailyplan,
    )

    if share.removed or share.dismissed:
        share.removed = False
        share.dismissed = False
        share.save(update_fields=["removed", "dismissed"])

    return DailyPlanShareCreateResult(
        share=share,
        created=created,
    )


@transaction.atomic
def accept_dailyplan_share(
    *,
    share: DailyPlanShare,
    user,
) -> DailyPlanShareAcceptResult:
    share.accepted_by = user
    share.dismissed = False
    share.removed = False
    share.save(
        update_fields=[
            "accepted_by",
            "dismissed",
            "removed",
        ]
    )

    return DailyPlanShareAcceptResult(
        share=share,
    )


@transaction.atomic
def dismiss_dailyplan_share(
    *,
    share: DailyPlanShare,
) -> DailyPlanShareDismissResult:
    share.dismissed = True
    share.save(update_fields=["dismissed"])

    return DailyPlanShareDismissResult(
        share=share,
    )


@transaction.atomic
def remove_dailyplan_share(
    *,
    share: DailyPlanShare,
) -> DailyPlanShareRemoveResult:
    share.removed = True
    share.save(update_fields=["removed"])

    return DailyPlanShareRemoveResult(
        share=share,
    )



@transaction.atomic
def create_meal_share(
    *,
    sender,
    meal: Meal,
    recipient_email: str,
) -> MealShareCreateResult:
    clean_email = (recipient_email or "").strip().lower()

    if not clean_email:
        raise ValueError("recipient_email_required")

    share, created = MealShare.objects.get_or_create(
        sender=sender,
        recipient_email=clean_email,
        meal=meal,
    )

    if share.removed or share.dismissed:
        share.removed = False
        share.dismissed = False
        share.save(update_fields=["removed", "dismissed"])

    return MealShareCreateResult(
        share=share,
        created=created,
    )


@transaction.atomic
def accept_meal_share(
    *,
    share: MealShare,
    user,
) -> MealShareAcceptResult:
    share.accepted_by = user
    share.dismissed = False
    share.removed = False
    share.save(
        update_fields=[
            "accepted_by",
            "dismissed",
            "removed",
        ]
    )

    return MealShareAcceptResult(
        share=share,
    )


@transaction.atomic
def dismiss_meal_share(
    *,
    share: MealShare,
) -> MealShareDismissResult:
    share.dismissed = True
    share.save(update_fields=["dismissed"])

    return MealShareDismissResult(
        share=share,
    )


@transaction.atomic
def remove_meal_share(
    *,
    share: MealShare,
) -> MealShareRemoveResult:
    share.removed = True
    share.save(update_fields=["removed"])

    return MealShareRemoveResult(
        share=share,
    )