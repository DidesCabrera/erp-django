from django.urls import reverse
from notas.application.resolvers.dailyplan_meal_resolvers import resolve_dailyplan_meal_actions
from notas.application.resolvers.dailyplan_resolvers import resolve_dailyplan_actions
from notas.application.resolvers.meal_resolvers import resolve_meal_actions
from notas.application.resolvers.food_resolvers import resolve_food_actions
from notas.presentation.config.viewmodel_config import *


def build_food_header(*, food, user, viewmode):
    actions = resolve_food_actions(
            food,
            user,
            viewmode
        )

    return {
        "title": food.name,
        "actions": actions,
    }


def build_meal_header(*, meal, user, viewmode):
    actions = resolve_meal_actions(
            meal,
            user,
            viewmode
        )

    return {
        "title": meal.name,
        "actions": actions,
    }


def build_dailyplan_meal_header(*, dpm, user, viewmode):
    meal = dpm.meal
    actions = resolve_dailyplan_meal_actions(
            dpm,
            user,
            viewmode
        )

    return {
        "title": meal.name,
        "actions": actions,
    }


def build_dailyplan_header(*, dailyplan, user, viewmode):

    actions = resolve_dailyplan_actions(
            dailyplan,
            user,
            viewmode
        )
    
    return {
        "actions": actions,
    }
