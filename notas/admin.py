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