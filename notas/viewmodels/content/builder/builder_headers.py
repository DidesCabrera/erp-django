from django.urls import reverse
from notas.actions.dailyplan_meal_resolvers import resolve_dailyplan_meal_actions
from notas.actions.dailyplan_resolvers import resolve_dailyplan_actions
from notas.actions.meal_resolvers import resolve_meal_actions
from notas.actions.constants import *





def build_meal_header(*, meal, user, context_name):

    navigation = [
        {"label": "Meals", "url": reverse("meal_list")},
        {"label": meal.name, "url": None},
    ]

    actions = resolve_meal_actions(
            meal,
            user,
            context={
                "name": context_name
            },
        )

    return {
        "title": meal.name,
        "navigation": navigation,
        "actions": actions,
    }


def build_dailyplan_meal_header(*, dpm, user, context_name):
    dailyplan = dpm.dailyplan
    meal = dpm.meal

    navigation = [
        {"label": "Daily Plans", "url": reverse("dailyplan_list")},
        {"label": dailyplan.name, "url": reverse("dailyplan_detail", args=[dailyplan.id])},
        {"label": meal.name, "url": None},
    ]

    return {
        "title": meal.name,
        "navigation": navigation,
        "actions": resolve_dailyplan_meal_actions(
            dpm,
            user,
            context={"name": context_name},
        )
    }


def build_dailyplan_header(*, dailyplan, user, context_name):

    actions = resolve_dailyplan_actions(
            dailyplan,
            user,
            context={
                "name": context_name
            },
        )
    
    return {
        "actions": actions,
    }
