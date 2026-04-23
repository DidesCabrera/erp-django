from dataclasses import dataclass
from typing import Any

from notas.domain.models import Food
from notas.presentation.config.viewmodel_config import FOOD_VIEWMODE_PERSONAL_LIST
from notas.application.resolvers.food_resolvers import resolve_food_page_actions


@dataclass
class FoodListPageData:
    foods: Any
    page_actions: list
    viewmode: Any


def get_food_list_page_data(user) -> FoodListPageData:
    foods = (
        Food.objects
        .filter(created_by=user)
        .order_by("name")
    )

    viewmode = FOOD_VIEWMODE_PERSONAL_LIST

    page_actions = resolve_food_page_actions(
        user,
        viewmode,
    )

    return FoodListPageData(
        foods=foods,
        page_actions=page_actions,
        viewmode=viewmode,
    )