from django.db.models import Case, IntegerField, Q, QuerySet, Value, When

from notas.domain.models import Food


def get_food_picker_queryset(user) -> QuerySet:
    """
    Return foods available for food picker surfaces.

    Includes:
    - foods created by the current user;
    - global visible foods;
    - legacy system foods created without user, if visible.

    Excludes:
    - private foods from other users;
    - inactive global/system foods;
    - hidden global/system foods;
    - rejected global/system foods.

    Ordering rule:
    1. user foods
    2. core global/system foods
    3. extended global/system foods
    4. verified before non-verified
    5. name
    6. id

    This query is intentionally UI-safe but does not change the payload shape yet.
    Badges and visual labels belong to a later block.
    """

    visible_global_values = [
        Food.VISIBILITY_CORE,
        Food.VISIBILITY_EXTENDED,
    ]

    return (
        Food.objects
        .filter(
            Q(created_by=user)
            | Q(
                Q(is_global=True) | Q(created_by__isnull=True),
                is_active=True,
                visibility__in=visible_global_values,
            )
        )
        .annotate(
            picker_source_priority=Case(
                When(created_by=user, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            picker_visibility_priority=Case(
                When(visibility=Food.VISIBILITY_CORE, then=Value(0)),
                When(visibility=Food.VISIBILITY_EXTENDED, then=Value(1)),
                default=Value(9),
                output_field=IntegerField(),
            ),
            picker_verified_priority=Case(
                When(is_verified=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
        )
        .distinct()
        .order_by(
            "picker_source_priority",
            "picker_visibility_priority",
            "picker_verified_priority",
            "name",
            "id",
        )
    )