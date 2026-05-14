from django.contrib import messages

from notas.domain.models import Food


def _update_foods(modeladmin, request, queryset, *, update_fields: dict, message: str):
    updated = queryset.update(**update_fields)

    modeladmin.message_user(
        request,
        f"{updated} food(s) updated: {message}",
        messages.SUCCESS,
    )


def mark_foods_as_core(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "visibility": Food.VISIBILITY_CORE,
            "is_active": True,
        },
        message="marked as core and active.",
    )


mark_foods_as_core.short_description = "Mark selected foods as core"


def mark_foods_as_extended(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "visibility": Food.VISIBILITY_EXTENDED,
            "is_active": True,
        },
        message="marked as extended and active.",
    )


mark_foods_as_extended.short_description = "Mark selected foods as extended"


def mark_foods_as_hidden(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "visibility": Food.VISIBILITY_HIDDEN,
        },
        message="marked as hidden.",
    )


mark_foods_as_hidden.short_description = "Mark selected foods as hidden"


def mark_foods_as_rejected(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "visibility": Food.VISIBILITY_REJECTED,
            "is_active": False,
        },
        message="marked as rejected and inactive.",
    )


mark_foods_as_rejected.short_description = "Mark selected foods as rejected"


def mark_foods_as_verified(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "is_verified": True,
        },
        message="marked as verified.",
    )


mark_foods_as_verified.short_description = "Mark selected foods as verified"


def mark_foods_as_unverified(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "is_verified": False,
        },
        message="marked as unverified.",
    )


mark_foods_as_unverified.short_description = "Mark selected foods as unverified"


def mark_foods_as_active(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "is_active": True,
        },
        message="marked as active.",
    )


mark_foods_as_active.short_description = "Mark selected foods as active"


def mark_foods_as_inactive(modeladmin, request, queryset):
    _update_foods(
        modeladmin,
        request,
        queryset,
        update_fields={
            "is_active": False,
        },
        message="marked as inactive.",
    )


mark_foods_as_inactive.short_description = "Mark selected foods as inactive"