from notas.application.resolvers.dailyplan_meal_resolvers import resolve_dailyplan_meal_actions
from notas.application.resolvers.dailyplan_resolvers import resolve_dailyplan_actions
from notas.application.resolvers.meal_resolvers import resolve_meal_actions
from notas.application.resolvers.food_resolvers import resolve_food_actions
from notas.presentation.viewmodels.components.header_vm import HeaderVM, HeaderActionVM


def _build_header_actions(actions_data):
    return [
        HeaderActionVM(
            key=action["key"],
            label=action["label"],
            url=action["url"],
            method=action.get("method", "get"),
            group=action.get("group", "primary"),
            icon=action.get("icon"),
            is_back=action.get("is_back", False),
            order=action.get("order", 0),
        )
        for action in actions_data
    ]


def build_food_header(*, food, user, viewmode):
    actions = resolve_food_actions(
        food,
        user,
        viewmode,
    )

    return HeaderVM(
        title=food.name,
        actions=_build_header_actions(actions),
    )


def build_meal_header(*, meal, user, viewmode):
    actions = resolve_meal_actions(
        meal,
        user,
        viewmode,
    )

    return HeaderVM(
        title=meal.name,
        actions=_build_header_actions(actions),
    )


def build_dailyplan_meal_header(*, dpm, user, viewmode):
    meal = dpm.meal
    actions = resolve_dailyplan_meal_actions(
        dpm,
        user,
        viewmode,
    )

    return HeaderVM(
        title=meal.name,
        actions=_build_header_actions(actions),
    )


def build_dailyplan_header(*, dailyplan, user, viewmode):
    actions = resolve_dailyplan_actions(
        dailyplan,
        user,
        viewmode,
    )

    return HeaderVM(
        title="",
        actions=_build_header_actions(actions),
    )