from django.urls import reverse
from notas.actions.dailyplan_meal_resolvers import resolve_dailyplan_meal_actions
from notas.actions.dailyplan_resolvers import resolve_dailyplan_actions
from notas.actions.meal_resolvers import resolve_meal_actions
from notas.viewmodels.list_vm import ListHeaderUI
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

    nav_context = "meal"

    return {
        "title": meal.name,
        "navigation": navigation,
        "actions": actions,
        "nav_context" : nav_context
    }


def build_dailyplan_meal_header(*, dpm, user, context_name):
    dailyplan = dpm.dailyplan
    meal = dpm.meal
    nav_context = "dailyplan"

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
        ),
        "nav_context": nav_context
    }


def build_dailyplan_header(*, dailyplan, user, context_name):

    navigation = [
        {"label": "Daily Plans", "url": reverse("dailyplan_list")},
        {"label": dailyplan.name, "url": None},
    ]

    actions = resolve_dailyplan_actions(
            dailyplan,
            user,
            context={
                "name": context_name
            },
        )

    nav_context = "dailyplan"
    
    return {
        "title": dailyplan.name,
        "navigation": navigation,
        "actions": actions,
        "nav_context": nav_context
    }


def build_list_header(*, entity: str, context_name: str) -> ListHeaderUI:

    # DAILYPLAN =====================

    if entity == "dailyplan":

        if context_name == DAILYPLAN_VIEWMODE_LIST:
            return ListHeaderUI(
                title="Mis Planes Diarios",
                subtitle="Your personal library",
                nav_context="dailyplan"
            )

        if context_name == DAILYPLAN_VIEWMODE_EXPLORE_LIST:
            return ListHeaderUI(
                title="Planes Diarios: Explorar",
                subtitle="Plans shared by the community",
                nav_context="dailyplan"
            )

        if context_name == DAILYPLAN_VIEWMODE_SHARED_LIST:
            return ListHeaderUI(
                title="Planes Diarios: Compartidos conmigo",
                subtitle="Plans other users shared with you",
                nav_context="dailyplan"
            )

        if context_name == DAILYPLAN_VIEWMODE_DRAFT_LIST:
            return ListHeaderUI(
                title="Planes Diarios: Borradores",
                subtitle="Work in progress",
                nav_context="dailyplan"
            )

    
    # MEAL =======================
    
    if entity == "meal":

        if context_name == MEAL_VIEWMODE_LIST:
            return ListHeaderUI(
                title="Mis Comidas",
                subtitle="Your saved meals",
                nav_context="meal"
            )

        if context_name == MEAL_VIEWMODE_EXPLORE_LIST:
            return ListHeaderUI(
                title="Explorar Comidas",
                subtitle="Discover meals from others",
                nav_context="meal"
            )

        if context_name == MEAL_VIEWMODE_SHARED_LIST:
            return ListHeaderUI(
                title="Comidas compartidas conmigo",
                subtitle="Meals other users shared with you",
                nav_context="meal"
            )

        if context_name == MEAL_VIEWMODE_DRAFT_LIST:
            return ListHeaderUI(
                title="Borradores de Comidas",
                subtitle="Meals you are still building",
                nav_context="meal"
            )

    if entity == "food":

        if context_name == FOOD_VIEWMODE_LIST:
            return ListHeaderUI(
                title="Mis Alimentos",
                subtitle="Your saved meals",
                nav_context="food"
            )
    
    if entity == "inbox":

        return ListHeaderUI(
            title="Mis Notificaciones",
            subtitle="Your saved meals",
            nav_context="inbox"
        )

    if entity == "nutrition":

        return ListHeaderUI(
            title="Elementales",
            subtitle="Your saved meals",
            nav_context="nutrition"
        )








    # =========================
    # DEFAULT FALLBACK
    # =========================
    return ListHeaderUI(
        title="Library",
        subtitle=None
    )
