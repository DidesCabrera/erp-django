
from notas.models import DailyPlan
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from notas.services.nutrition import (
    PROTEIN_KCAL_PER_GRAM,
    CARBS_KCAL_PER_GRAM,
    FAT_KCAL_PER_GRAM,
)


def dailyplans_with_kcal():
    return (
        DailyPlan.objects
        .prefetch_related(
            "dailyplan_meals__meal__meal_food_set__food"
        )
        .annotate(
            total_kcal_sql=Sum(
                ExpressionWrapper(
                    (F("dailyplan_meals__meal__meal_food_set__quantity") / 100.0) * (
                        F("dailyplan_meals__meal__meal_food_set__food__protein") * PROTEIN_KCAL_PER_GRAM +
                        F("dailyplan_meals__meal__meal_food_set__food__carbs")   * CARBS_KCAL_PER_GRAM +
                        F("dailyplan_meals__meal__meal_food_set__food__fat")     * FAT_KCAL_PER_GRAM
                    ),
                    output_field=FloatField(),
                )
            )
        )
    )

def get_dailyplan_for_edit(user, pk):
    return (
        DailyPlan.objects
        .filter(pk=pk, created_by=user)
        .select_related("created_by", "original_author")
        .prefetch_related(
            "dailyplan_meals__meal",
            "dailyplan_meals__meal__meal_food_set",
            "dailyplan_meals__meal__meal_food_set__food",
        )
        .get()
    )

