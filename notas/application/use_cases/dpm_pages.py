from dataclasses import dataclass
from typing import Any, List, Optional
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404

from notas.domain.models import DailyPlanMeal, MealFood, Food
from notas.application.services.nutrition.nutrition_kpis import (
    build_nutrition_kpis_from_meal,
    build_nutrition_kpis_from_dailyplan,
    get_ppk_dailyplan,
    get_ppk_meal,
)
from notas.presentation.composition.js.food_picker_builder import (
    build_food_picker_foods_payload,
)
from notas.presentation.composition.js.dpm_food_picker_builder import (
    build_dpm_food_picker_context_payload,
)
from notas.presentation.composition.viewmodel.components.builder_table_items import (
    build_mealfood_table_item,
)
from notas.presentation.composition.viewmodel.components.builder_headers import (
    build_dailyplan_meal_header,
)
from notas.application.resolvers.meal_food_resolvers import (
    resolve_meal_food_actions,
)
from notas.presentation.config.icons import CONTENT_ICON_REGISTRY

from notas.presentation.resolvers.title_resolvers import resolve_category_badge


def _get_dpm_for_user(user, dailyplan_id: int, dpm_id: int):
    return get_object_or_404(
        DailyPlanMeal.objects
        .select_related("meal", "dailyplan")
        .prefetch_related(
            "meal__meal_food_set",
            "meal__meal_food_set__food",
        ),
        id=dpm_id,
        dailyplan_id=dailyplan_id,
        dailyplan__created_by=user,
    )


def _get_optional_editing_mealfood(request_get, meal):
    edit_mf_id = request_get.get("edit_food")
    mealfood = None

    if edit_mf_id:
        mealfood = get_object_or_404(
            MealFood,
            pk=edit_mf_id,
            meal=meal,
        )

    return edit_mf_id, mealfood


@dataclass
class DpmDetailPageData:
    dailyplan: Any
    dpm: Any
    meal: Any
    meal_foods: List[Any]
    detail_content_data: Any
    viewmode: Any


def get_dpm_detail_page_data(
    user,
    dailyplan_id: int,
    dpm_id: int,
    viewmode,
) -> DpmDetailPageData:
    dpm = _get_dpm_for_user(
        user=user,
        dailyplan_id=dailyplan_id,
        dpm_id=dpm_id,
    )

    dailyplan = dpm.dailyplan
    meal = dpm.meal
    meal_foods = list(meal.meal_food_set.select_related("food").all())

    detail_content_data = build_dpm_detail_content_data(
        dailyplan=dailyplan,
        dpm=dpm,
        meal=meal,
        meal_foods=meal_foods,
        user=user,
        viewmode=viewmode,
        header_builder=build_dailyplan_meal_header,
    )

    return DpmDetailPageData(
        dailyplan=dailyplan,
        dpm=dpm,
        meal=meal,
        meal_foods=meal_foods,
        detail_content_data=detail_content_data,
        viewmode=viewmode,
    )


@dataclass
class DpmEditPageData:
    dailyplan: Any
    dpm: Any
    meal: Any
    meal_foods: List[Any]
    detail_content_data: Any
    viewmode: Any


def get_dpm_edit_page_data(
    user,
    dailyplan_id: int,
    dpm_id: int,
    viewmode,
) -> DpmEditPageData:
    dpm = _get_dpm_for_user(
        user=user,
        dailyplan_id=dailyplan_id,
        dpm_id=dpm_id,
    )

    dailyplan = dpm.dailyplan
    meal = dpm.meal
    meal_foods = list(meal.meal_food_set.select_related("food").all())

    detail_content_data = build_dpm_detail_content_data(
        dailyplan=dailyplan,
        dpm=dpm,
        meal=meal,
        meal_foods=meal_foods,
        user=user,
        viewmode=viewmode,
        header_builder=build_dailyplan_meal_header,
    )

    return DpmEditPageData(
        dailyplan=dailyplan,
        dpm=dpm,
        meal=meal,
        meal_foods=meal_foods,
        detail_content_data=detail_content_data,
        viewmode=viewmode,
    )


@dataclass
class DpmDeepEditPageData:
    dailyplan: Any
    dpm: Any
    meal: Any
    meal_foods: List[Any]
    detail_content_data: Any
    selected_food_id: Optional[str]
    editing_mealfood_id: Optional[int]
    foods_json: str
    food_picker_context_json: str
    viewmode: Any


def get_dpm_deep_edit_page_data(
    user,
    dailyplan_id: int,
    dpm_id: int,
    request_get,
    viewmode,
) -> DpmDeepEditPageData:
    dpm = _get_dpm_for_user(
        user=user,
        dailyplan_id=dailyplan_id,
        dpm_id=dpm_id,
    )

    dailyplan = dpm.dailyplan
    meal = dpm.meal
    meal_foods = list(meal.meal_food_set.select_related("food").all())

    edit_mf_id, mealfood = _get_optional_editing_mealfood(
        request_get=request_get,
        meal=meal,
    )

    foods_payload = build_food_picker_foods_payload(
        Food.objects.all()
    )

    meal_kpis = build_nutrition_kpis_from_meal(
        meal,
        user,
    )

    dailyplan_kpis = build_nutrition_kpis_from_dailyplan(
        dailyplan,
        user,
    )

    food_picker_ctx = build_dpm_food_picker_context_payload(
        meal=meal,
        meal_kpis=meal_kpis,
        dailyplan=dailyplan,
        dailyplan_kpis=dailyplan_kpis,
        mealfood=mealfood,
    )

    detail_content_data = build_dpm_detail_content_data(
        dailyplan=dailyplan,
        dpm=dpm,
        meal=meal,
        meal_foods=meal_foods,
        user=user,
        viewmode=viewmode,
        header_builder=build_dailyplan_meal_header,
    )

    return DpmDeepEditPageData(
        dailyplan=dailyplan,
        dpm=dpm,
        meal=meal,
        meal_foods=meal_foods,
        detail_content_data=detail_content_data,
        selected_food_id=request_get.get("select_food"),
        editing_mealfood_id=int(edit_mf_id) if edit_mf_id else None,
        foods_json=json.dumps(
            foods_payload.as_list(),
            cls=DjangoJSONEncoder,
        ),
        food_picker_context_json=json.dumps(
            food_picker_ctx.as_dict(),
            cls=DjangoJSONEncoder,
        ),
        viewmode=viewmode,
    )


@dataclass
class DpmDetailContentData:
    header: Any
    father_card_data: dict
    main_card_data: dict
    child_cards_data: list
    structural_indicators: dict


def build_dpm_detail_content_data(
    dailyplan,
    dpm,
    meal,
    meal_foods,
    user,
    viewmode,
    header_builder,
):
    # ==================================================
    # HEADER
    # ==================================================
    header = header_builder(
        dpm=dpm,
        user=user,
        viewmode=viewmode,
    )

    # ==================================================
    # DAILYPLAN AGGREGATES
    # ==================================================
    dp_total_kcal = dailyplan.total_kcal
    dp_protein = dailyplan.protein
    dp_carbs = dailyplan.carbs
    dp_fat = dailyplan.fat

    dp_kcal_protein = dailyplan.kcal_protein
    dp_kcal_carbs = dailyplan.kcal_carbs
    dp_kcal_fat = dailyplan.kcal_fat

    dp_alloc = dailyplan.alloc

    father_ppk = get_ppk_dailyplan(dailyplan, user)

    # ==================================================
    # MEAL AGGREGATES
    # ==================================================
    meal_total_kcal = meal.total_kcal_cached or meal.total_kcal
    meal_protein = meal.protein_cached or meal.protein
    meal_carbs = meal.carbs_cached or meal.carbs
    meal_fat = meal.fat_cached or meal.fat

    meal_kcal_protein = meal.kcal_protein_cached or meal.kcal_protein
    meal_kcal_carbs = meal.kcal_carbs_cached or meal.kcal_carbs
    meal_kcal_fat = meal.kcal_fat_cached or meal.kcal_fat

    meal_alloc = {
        "protein": meal.alloc_protein_cached or meal.alloc["protein"],
        "carbs": meal.alloc_carbs_cached or meal.alloc["carbs"],
        "fat": meal.alloc_fat_cached or meal.alloc["fat"],
    }

    meal_ppk = get_ppk_meal(meal, user)

    meal_foods_table_items = [
        build_mealfood_table_item(mf)
        for mf in meal_foods
    ]

    structural_indicators = {
        "foods_count": len(meal_foods),
    }

    father_card_data = {
        "father_id": dailyplan.id,
        "title": {
            "name": dailyplan.name,
            "label": "Daily Plan",
            "category": dailyplan.category,
            "category_badge": resolve_category_badge(meal.category),
            "icon": CONTENT_ICON_REGISTRY.get("dailyplan"),
        },
        "rel_id": dpm.id,
        "kpis": {
            "ppk": father_ppk["ppk"],
            "tot_kcal": dp_total_kcal,
            "g_protein": dp_protein,
            "g_carbs": dp_carbs,
            "g_fat": dp_fat,
            "kcal_protein": dp_kcal_protein,
            "kcal_carbs": dp_kcal_carbs,
            "kcal_fat": dp_kcal_fat,
            "alloc_protein": dp_alloc["protein"],
            "alloc_carbs": dp_alloc["carbs"],
            "alloc_fat": dp_alloc["fat"],
        },
        "related_data": {
            "rel_id": dpm.id,
            "hour": str(dpm.hour) if dpm.hour else None,
            "note": dpm.note,
            "alloc_protein": meal_alloc["protein"],
            "alloc_carbs": meal_alloc["carbs"],
            "alloc_fat": meal_alloc["fat"],
        },
    }

    main_card_data = {
        "main_id": meal.id,
        "title": {
            "name": meal.name,
            "label": "Meal",
            "icon": CONTENT_ICON_REGISTRY.get("meal"),
            "category": meal.category,
            "category_badge": resolve_category_badge(meal.category),
        },
        "kpis": {
            "ppk": meal_ppk["ppk"],
            "tot_kcal": meal_total_kcal,
            "g_protein": meal_protein,
            "g_carbs": meal_carbs,
            "g_fat": meal_fat,
            "kcal_protein": meal_kcal_protein,
            "kcal_carbs": meal_kcal_carbs,
            "kcal_fat": meal_kcal_fat,
            "alloc_protein": meal_alloc["protein"],
            "alloc_carbs": meal_alloc["carbs"],
            "alloc_fat": meal_alloc["fat"],
        },
        "table_items": meal_foods_table_items,
        "metadata": {
            "owner": str(meal.created_by),
            "author": str(meal.original_author),
            "fork_from": str(meal.forked_from) if meal.forked_from else None,
        },
    }

    child_cards_data = []

    for mf in meal_foods:
        food = mf.food
        food_alloc = food.alloc

        child_cards_data.append(
            {
                "child_id": food.id,
                "related_data": {
                    "rel_id": mf.id,
                    "quantity": mf.quantity,
                    "alloc_protein": food_alloc["protein"],
                    "alloc_carbs": food_alloc["carbs"],
                    "alloc_fat": food_alloc["fat"],
                },
                "title": {
                    "name": food.name,
                    "label": "Food",
                    "icon": CONTENT_ICON_REGISTRY.get("food"),
                    "category": getattr(food, "category", None),
                    "category_badge": resolve_category_badge(food.category),
                },
                "kpis": {
                    "ppk": meal_ppk["ppk"],
                    "tot_kcal": food.total_kcal,
                    "g_protein": food.protein,
                    "g_carbs": food.carbs,
                    "g_fat": food.fat,
                    "kcal_protein": food.kcal_protein,
                    "kcal_carbs": food.kcal_carbs,
                    "kcal_fat": food.kcal_fat,
                    "alloc_protein": food_alloc["protein"],
                    "alloc_carbs": food_alloc["carbs"],
                    "alloc_fat": food_alloc["fat"],
                },
                "actions": resolve_meal_food_actions(
                    mf,
                    user,
                    viewmode,
                ),
            }
        )

    return DpmDetailContentData(
        header=header,
        father_card_data=father_card_data,
        main_card_data=main_card_data,
        child_cards_data=child_cards_data,
        structural_indicators=structural_indicators,
    )