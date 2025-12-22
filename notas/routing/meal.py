from django.urls import reverse


def meal_url(meal, *, dailyplan=None):

    if dailyplan:
        return reverse(
            "dailyplan_meal_detail",
            args=[dailyplan.id, meal.id],
        )

    # canonical / neutral URL
    return meal.get_canonical_url()

