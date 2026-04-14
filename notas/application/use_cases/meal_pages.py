from dataclasses import dataclass
from typing import Any, List, Optional
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404

from notas.application.services.access.access import get_meal_for_user
from notas.domain.models import Meal, MealFood, Food
from notas.presentation.config.viewmodel_config import (
    MEAL_VIEWMODE_PERSONAL_DETAIL,
    MEAL_VIEWMODE_EXPLORE_DETAIL,
    MEAL_VIEWMODE_SHARED_DETAIL,
    MEAL_VIEWMODE_DRAFT_DETAIL,
    MEAL_VIEWMODE_PERSONAL_LIST,
    MEAL_VIEWMODE_EXPLORE_LIST,
    MEAL_VIEWMODE_SHARED_LIST,
    MEAL_VIEWMODE_DRAFT_LIST,
)

from notas.application.services.nutrition.nutrition_kpis import build_nutrition_kpis_from_meal
from notas.presentation.composition.js.food_picker_builder import (
    build_food_picker_context_payload,
    build_food_picker_foods_payload,
)


from notas.application.services.nutrition.nutrition_kpis import get_ppk_meal
from notas.presentation.composition.viewmodel.components.builder_headers import build_meal_header
from notas.presentation.composition.viewmodel.components.builder_table_items import build_mealfood_table_item
from notas.presentation.composition.viewmodel.components.builder_foods_aggregation import build_meal_foods_aggregation
from notas.application.resolvers.meal_resolvers import resolve_meal_actions
from notas.application.resolvers.meal_food_resolvers import resolve_meal_food_actions
from notas.presentation.config.icons import CONTENT_ICON_REGISTRY

from notas.presentation.resolvers.title_resolvers import resolve_category_badge


@dataclass
class MealDetailPageData:
    meal: Any
    meal_foods: List[Any]
    detail_content_data: Any
    viewmode: Any

def get_meal_detail_page_data(
    user,
    meal_id: int,
    viewmode,
) -> MealDetailPageData:

    meal = get_meal_for_user(user, meal_id)
    meal_foods = list(meal.meal_food_set.all())

    detail_content_data = build_meal_detail_content_data(
        meal=meal,
        user=user,
        viewmode=viewmode,
        header_builder=build_meal_header,
        build_mealfood_table_item=build_mealfood_table_item,
        build_meal_foods_aggregation=build_meal_foods_aggregation,
        resolve_meal_actions=resolve_meal_actions,
        content_icon_registry=CONTENT_ICON_REGISTRY,
    )

    return MealDetailPageData(
        meal=meal,
        meal_foods=meal_foods,
        detail_content_data=detail_content_data,
        viewmode=viewmode,
    )


@dataclass
class MealDetailContentData:
    header: Any
    main_card_data: dict
    structural_indicators: dict
    table_items: list
    child_cards_data: list


def build_meal_detail_content_data(
    meal,
    user,
    viewmode,
    header_builder,
    build_mealfood_table_item,
    build_meal_foods_aggregation,
    resolve_meal_actions,
    content_icon_registry,
):
    # ==================================================
    # HEADER
    # ==================================================
    header = header_builder(
        meal=meal,
        user=user,
        viewmode=viewmode,
    )

    # ==================================================
    # MAIN AGGREGATES
    # ==================================================
    meal_total_kcal = meal.total_kcal_cached or meal.total_kcal
    meal_protein = meal.protein_cached or meal.protein
    meal_carbs = meal.carbs_cached or meal.carbs
    meal_fat = meal.fat_cached or meal.fat

    meal_alloc = {
        "protein": meal.alloc_protein_cached or meal.alloc["protein"],
        "carbs": meal.alloc_carbs_cached or meal.alloc["carbs"],
        "fat": meal.alloc_fat_cached or meal.alloc["fat"],
    }

    ppk = get_ppk_meal(meal, user)

    meal_foods = list(meal.meal_food_set.select_related("food").all())

    table_items = [
        build_mealfood_table_item(mf)
        for mf in meal_foods
    ]

    foods_aggregation = build_meal_foods_aggregation(meal)

    main_card_data = {
        "main_id": meal.id,
        "title": {
            "name": meal.name,
            "label": "Meal",
            "icon": content_icon_registry.get("meal"),
            "category": meal.category,
            "category_badge": resolve_category_badge(meal.category),
            "foods_count": len(foods_aggregation),
        },
        "kpis": {
            "ppk": ppk["ppk"],
            "tot_kcal": meal_total_kcal,
            "g_protein": meal_protein,
            "g_carbs": meal_carbs,
            "g_fat": meal_fat,
            "kcal_protein": meal.kcal_protein_cached or meal.kcal_protein,
            "kcal_carbs": meal.kcal_carbs_cached or meal.kcal_carbs,
            "kcal_fat": meal.kcal_fat_cached or meal.kcal_fat,
            "alloc_protein": meal_alloc["protein"],
            "alloc_carbs": meal_alloc["carbs"],
            "alloc_fat": meal_alloc["fat"],
        },
        "foods_aggregation": foods_aggregation,
        "metadata": {
            "owner": str(meal.created_by),
            "author": str(meal.original_author),
            "fork_from": str(meal.forked_from) if meal.forked_from else None,
        },
        "show_kpis": len(meal_foods) > 0,
        "show_table": len(meal_foods) > 0,
    }

    structural_indicators = {
        "foods_count": len(meal_foods),
    }

    # ==================================================
    # CHILD CARDS = MEALFOODS
    # ==================================================
    child_cards_data = []

    for mf in meal_foods:
        food = mf.food

        qty_factor = float(mf.quantity) / 100.0

        food_total_kcal = float(food.total_kcal) * qty_factor
        food_protein = float(food.protein) * qty_factor
        food_carbs = float(food.carbs) * qty_factor
        food_fat = float(food.fat) * qty_factor

        food_alloc = food.alloc

        child_cards_data.append(
            {
                "child_id": food.id,
                "related_data": {
                    "rel_id": mf.id,
                    "quantity": float(mf.quantity),
                    "alloc_protein": float(food_alloc["protein"]),
                    "alloc_carbs": float(food_alloc["carbs"]),
                    "alloc_fat": float(food_alloc["fat"]),
                },
                "title": {
                    "name": food.name,
                    "label": "Food",
                    "icon": content_icon_registry.get("food"),
                    "category": getattr(food, "category", None),
                    "category_badge": resolve_category_badge(getattr(food, "category", None)),
                },
                "kpis": {
                    "ppk": 0,
                    "tot_kcal": food_total_kcal,
                    "g_protein": food_protein,
                    "g_carbs": food_carbs,
                    "g_fat": food_fat,
                    "kcal_protein": food_protein * 4,
                    "kcal_carbs": food_carbs * 4,
                    "kcal_fat": food_fat * 9,
                    "alloc_protein": float(food_alloc["protein"]),
                    "alloc_carbs": float(food_alloc["carbs"]),
                    "alloc_fat": float(food_alloc["fat"]),
                },
                "actions": resolve_meal_food_actions(
                    mf,
                    user,
                    viewmode,
                ),
            }
        )

    return MealDetailContentData(
        header=header,
        main_card_data=main_card_data,
        structural_indicators=structural_indicators,
        table_items=table_items,
        child_cards_data=child_cards_data,
    )



@dataclass
class MealListContentData:
    child_cards_data: list

def build_meal_list_content_data(meals, user, viewmode):

    child_cards_data = []

    for meal in meals:
        meal_total_kcal = meal.total_kcal_cached or meal.total_kcal
        meal_protein = meal.protein_cached or meal.protein
        meal_carbs = meal.carbs_cached or meal.carbs
        meal_fat = meal.fat_cached or meal.fat

        meal_alloc = {
            "protein": meal.alloc_protein_cached or meal.alloc["protein"],
            "carbs": meal.alloc_carbs_cached or meal.alloc["carbs"],
            "fat": meal.alloc_fat_cached or meal.alloc["fat"],
        }

        ppk = get_ppk_meal(meal, user)

        meal_foods = list(meal.meal_food_set.all())

        table_items = [
            build_mealfood_table_item(mf)
            for mf in meal_foods
        ]

        foods_aggregation = build_meal_foods_aggregation(meal)

        actions = resolve_meal_actions(
            meal,
            user,
            viewmode,
        )

        child_cards_data.append(
            {
                "child_id": meal.id,
                "title": {
                    "name": meal.name,
                    "label": "Meal",
                    "icon": CONTENT_ICON_REGISTRY.get("meal"),
                    "category": meal.category,
                    "category_badge": resolve_category_badge(meal.category),
                    "foods_count": len(foods_aggregation),
                },
                "kpis": {
                    "ppk": ppk["ppk"],
                    "tot_kcal": meal_total_kcal,
                    "g_protein": meal_protein,
                    "g_carbs": meal_carbs,
                    "g_fat": meal_fat,
                    "kcal_protein": meal.kcal_protein_cached or meal.kcal_protein,
                    "kcal_carbs": meal.kcal_carbs_cached or meal.kcal_carbs,
                    "kcal_fat": meal.kcal_fat_cached or meal.kcal_fat,
                    "alloc_protein": meal_alloc["protein"],
                    "alloc_carbs": meal_alloc["carbs"],
                    "alloc_fat": meal_alloc["fat"],
                },
                "table_items": table_items,
                "foods_aggregation": foods_aggregation,
                "metadata": {
                    "owner": str(meal.created_by),
                    "author": str(meal.original_author),
                    "fork_from": str(meal.forked_from) if meal.forked_from else None,
                },
                "actions": actions,
            }
        )

    return MealListContentData(
        child_cards_data=child_cards_data,
    )



@dataclass
class MealListPageData:
    meals: Any
    list_content_data: Any
    viewmode: Any

def get_meal_list_page_data(user) -> MealListPageData:
    meals = (
        Meal.objects
        .filter(
            created_by=user,
            is_draft=False,
            dailyplanmeal__isnull=True,
        )
        .order_by("-created_at")
        .distinct()
    )

    viewmode = MEAL_VIEWMODE_PERSONAL_LIST

    list_content_data = build_meal_list_content_data(
        meals=meals,
        user=user,
        viewmode=viewmode,
    )

    return MealListPageData(
        meals=meals,
        list_content_data=list_content_data,
        viewmode=viewmode,
    )

def get_meal_explore_list_page_data(user) -> MealListPageData:
    meals = (
        Meal.objects
        .filter(
            is_public=True,
            is_draft=False,
            dailyplanmeal__isnull=True,
        )
        .order_by("-created_at")
        .distinct()
    )

    viewmode = MEAL_VIEWMODE_EXPLORE_LIST

    list_content_data = build_meal_list_content_data(
        meals=meals,
        user=user,
        viewmode=viewmode,
    )

    return MealListPageData(
        meals=meals,
        list_content_data=list_content_data,
        viewmode=viewmode,
    )

def get_meal_shared_list_page_data(user) -> MealListPageData:
    meals = (
        Meal.objects
        .filter(
            shares__accepted_by=user,
            shares__removed=False,
            is_draft=False,
            dailyplanmeal__isnull=True,
        )
        .prefetch_related("shares")
        .distinct()
    )

    viewmode = MEAL_VIEWMODE_SHARED_LIST

    list_content_data = build_meal_list_content_data(
        meals=meals,
        user=user,
        viewmode=viewmode,
    )

    return MealListPageData(
        meals=meals,
        list_content_data=list_content_data,
        viewmode=viewmode,
    )

def get_meal_draft_list_page_data(user) -> MealListPageData:
    meals = (
        Meal.objects
        .filter(
            created_by=user,
            is_draft=True,
            dailyplanmeal__isnull=True,
        )
        .order_by("-created_at")
        .distinct()
    )

    viewmode = MEAL_VIEWMODE_DRAFT_LIST

    list_content_data = build_meal_list_content_data(
        meals=meals,
        user=user,
        viewmode=viewmode,
    )

    return MealListPageData(
        meals=meals,
        list_content_data=list_content_data,
        viewmode=viewmode,
    )


@dataclass
class MealEditPageData:
    meal: Any
    meal_foods: List[Any]
    detail_content_data: Any
    selected_food_id: Optional[str]
    editing_mealfood_id: Optional[int]
    foods_json: str
    food_picker_context_json: str
    show_return_to_dailyplan: bool
    viewmode: Any

def get_meal_edit_page_data(
    user,
    meal_id: int,
    request_get,
    personal_edit_viewmode,
    personal_edit_from_dailyplan_viewmode,
) -> MealEditPageData:

    # ==================================================
    # Aggregate load
    # ==================================================
    meal = (
        Meal.objects
        .prefetch_related("meal_food_set", "meal_food_set__food")
        .get(pk=meal_id, created_by=user)
    )

    meal_foods = list(meal.meal_food_set.all())

    # ==================================================
    # Edit state
    # ==================================================
    edit_mf_id = request_get.get("edit_food")
    mealfood = None

    if edit_mf_id:
        mealfood = get_object_or_404(
            MealFood,
            pk=edit_mf_id,
            meal=meal,
        )

    # ==================================================
    # Food picker payload
    # ==================================================
    foods_payload = build_food_picker_foods_payload(
        Food.objects.all()
    )

    nutrition_kpis = build_nutrition_kpis_from_meal(
        meal,
        user,
    )

    food_picker_ctx = build_food_picker_context_payload(
        meal=meal,
        nutrition_kpis=nutrition_kpis,
        mealfood=mealfood,
    )

    # ==================================================
    # Viewmode
    # ==================================================
    if meal.pending_dailyplan:
        viewmode = personal_edit_from_dailyplan_viewmode
    else:
        viewmode = personal_edit_viewmode

    # ==================================================
    # Front payloads
    # ==================================================
    foods_json = json.dumps(
        foods_payload.as_list(),
        cls=DjangoJSONEncoder,
    )

    food_picker_context_json = json.dumps(
        food_picker_ctx.as_dict(),
        cls=DjangoJSONEncoder,
    )

    detail_content_data = build_meal_detail_content_data(
        meal=meal,
        user=user,
        viewmode=viewmode,
        header_builder=build_meal_header,
        build_mealfood_table_item=build_mealfood_table_item,
        build_meal_foods_aggregation=build_meal_foods_aggregation,
        resolve_meal_actions=resolve_meal_actions,
        content_icon_registry=CONTENT_ICON_REGISTRY,
    )

    return MealEditPageData(
        meal=meal,
        meal_foods=meal_foods,
        selected_food_id=request_get.get("select_food"),
        editing_mealfood_id=int(edit_mf_id) if edit_mf_id else None,
        foods_json=foods_json,
        food_picker_context_json=food_picker_context_json,
        show_return_to_dailyplan=(
            meal.pending_dailyplan is not None
            and not meal.is_draft
        ),
        viewmode=viewmode,
        detail_content_data=detail_content_data,
    )