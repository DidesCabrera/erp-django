from django.contrib import admin
from .domain.models import (
    Profile,
    Plan,
    Subscription,
    Food,
    Meal,
    MealFood,
    DailyPlan,
    DailyPlanMeal,
    NutritionProposal,
    NutritionProposalAuditEvent,
    Program,
    ProgramDay,
    WeightLog,
)

admin.site.register(Profile)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(Food)
admin.site.register(MealFood)
admin.site.register(DailyPlanMeal)
admin.site.register(Program)
admin.site.register(ProgramDay)
admin.site.register(WeightLog)

@admin.register(NutritionProposal)
class NutritionProposalAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "dailyplan",
        "status",
        "source",
        "created_by",
        "reviewed_by",
        "applied_by",
        "created_at",
        "reviewed_at",
        "applied_at",
    )
    list_filter = (
        "status",
        "source",
        "created_at",
        "reviewed_at",
        "applied_at",
    )
    search_fields = (
        "title",
        "summary",
        "dailyplan__name",
        "created_by__username",
        "reviewed_by__username",
        "applied_by__username",
    )
    readonly_fields = (
        "created_at",
        "reviewed_at",
        "applied_at",
    )

@admin.register(NutritionProposalAuditEvent)
class NutritionProposalAuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "proposal",
        "action",
        "actor",
        "status_before",
        "status_after",
        "created_at",
    )
    list_filter = (
        "action",
        "created_at",
    )
    search_fields = (
        "proposal__title",
        "actor__username",
        "message",
    )
    readonly_fields = (
        "created_at",
    )


class DailyPlanMealInline(admin.TabularInline):
    model = DailyPlanMeal
    fields = ('note', 'meal', 'hour', 'order')
    extra = 1

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    inlines = [DailyPlanMealInline]