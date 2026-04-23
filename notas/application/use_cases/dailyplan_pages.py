from dataclasses import dataclass
from typing import Optional, List, Any
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404

from notas.domain.models import DailyPlanMeal, Meal
from notas.application.services.queries.dailyplan_queries import (
    get_dailyplan_for_edit,
    dailyplans_with_kcal,
)
from notas.application.services.queries.meal_queries import meals_with_kcal
from notas.application.services.nutrition.nutrition_kpis import (
    build_nutrition_kpis_from_dailyplan,
    get_ppk_meal,
    get_ppk_dailyplan,
)
from notas.application.services.nutrition.meal_nutrition import rebuild_meal_cached_state
from notas.presentation.composition.js.meal_picker_builder import (
    build_meal_picker_context_payload,
    build_meal_picker_data_payload,
)
from notas.presentation.config.viewmodel_config import (
    DAILYPLAN_VIEWMODE_PERSONAL_LIST,
    DAILYPLAN_VIEWMODE_EXPLORE_LIST,
    DAILYPLAN_VIEWMODE_SHARED_LIST,
    DAILYPLAN_VIEWMODE_DRAFT_LIST,
    DAILYPLAN_VIEWMODE_PERSONAL_DETAIL,
)
from notas.application.services.access.access import get_dailyplan_for_user
from notas.presentation.composition.viewmodel.components.builder_table_items import (
    build_dailyplanmeal_table_item,
    build_mealfood_table_item,
)
from notas.presentation.composition.viewmodel.components.builder_foods_aggregation import (
    build_dailyplan_foods_aggregation,
    build_meal_foods_aggregation,
)
from notas.application.resolvers.dailyplan_meal_resolvers import (
    resolve_dailyplan_meal_actions,
)
from notas.presentation.config.icons import CONTENT_ICON_REGISTRY
from notas.presentation.composition.viewmodel.components.builder_headers import (
    build_dailyplan_header,
)
from notas.application.resolvers.share_resolvers import resolve_share_actions
from notas.presentation.composition.viewmodel.components.builder_menu import (
    build_dailyplan_menu,
)
from notas.presentation.resolvers.title_resolvers import resolve_category_badge
from notas.application.resolvers.dailyplan_resolvers import (
    resolve_dailyplan_entity_actions,
    resolve_dailyplan_page_actions,
)


def _meal_cache_is_missing(meal: Meal) -> bool:
    return any(
        value is None
        for value in [
            meal.protein_cached,
            meal.carbs_cached,
            meal.fat_cached,
            meal.total_kcal_cached,
            meal.alloc_protein_cached,
            meal.alloc_carbs_cached,
            meal.alloc_fat_cached,
            meal.foods_aggregation_cached,
        ]
    )


def _ensure_cached_state(meals):
    """
    Rehidrata cache solo si la meal tiene foods y su cache está incompleto.
    Evita que el picker use macros 0/null cuando la meal sí tiene contenido.
    """
    result = []

    for meal in meals:
        if meal.meal_food_set.exists() and _meal_cache_is_missing(meal):
            rebuild_meal_cached_state(meal)
            meal.refresh_from_db()

        result.append(meal)

    return result


@dataclass
class DailyPlanDetailPageData:
    dailyplan: Any
    dailyplan_meals: List[Any]
    detail_content_data: Any
    selected_meal_id: Optional[str] = None
    editing_dailyplanmeal_id: Optional[int] = None
    meal_picker_data_json: str = "{}"
    meal_picker_context_json: str = "{}"
    viewmode: Any = None


@dataclass
class DailyPlanDetailContentData:
    header: Any
    main_card_data: dict
    child_cards_data: list
    foods_aggregation: Any
    structural_indicators: dict


@dataclass
class DailyPlanListContentData:
    child_cards_data: list


@dataclass
class DailyPlanListPageData:
    dailyplans: Any
    list_content_data: Any
    page_actions: list
    viewmode: Any


def get_dailyplan_detail_page_data(
    user,
    dailyplan_id: int,
    viewmode,
    request_get=None,
) -> DailyPlanDetailPageData:
    request_get = request_get or {}

    selected_meal_id = None
    editing_dailyplanmeal_id = None
    meal_picker_data_json = "{}"
    meal_picker_context_json = "{}"
    effective_viewmode = viewmode

    if viewmode == DAILYPLAN_VIEWMODE_PERSONAL_DETAIL:
        dailyplan = get_dailyplan_for_edit(user, dailyplan_id)
        dailyplan_meals = list(dailyplan.meals_with_foods())

        edit_dpm_id = request_get.get("edit_meal")
        selected_meal_id = request_get.get("select_meal")

        dpm = None
        if edit_dpm_id:
            dpm = get_object_or_404(
                DailyPlanMeal.objects.select_related("meal"),
                pk=edit_dpm_id,
                dailyplan=dailyplan,
            )

        browse_meals_qs = (
            meals_with_kcal()
            .filter(
                created_by=user,
                is_draft=False,
                dailyplanmeal__isnull=True,
            )
            .order_by("-created_at")
            .distinct()
        )

        existing_meals_qs = (
            meals_with_kcal()
            .filter(
                dailyplanmeal__dailyplan=dailyplan,
            )
            .distinct()
        )

        browse_meals = _ensure_cached_state(list(browse_meals_qs))
        existing_meals = _ensure_cached_state(list(existing_meals_qs))

        meal_picker_data = build_meal_picker_data_payload(
            browse_meals_qs=browse_meals,
            existing_meals_qs=existing_meals,
        )

        dailyplan_kpis = build_nutrition_kpis_from_dailyplan(
            dailyplan,
            user,
        )

        meal_picker_context = build_meal_picker_context_payload(
            dailyplan=dailyplan,
            dailyplan_kpis=dailyplan_kpis,
            dpm=dpm,
        )

        meal_picker_data_json = json.dumps(
            meal_picker_data,
            cls=DjangoJSONEncoder,
        )

        meal_picker_context_json = json.dumps(
            meal_picker_context.as_dict(),
            cls=DjangoJSONEncoder,
        )

        editing_dailyplanmeal_id = int(edit_dpm_id) if edit_dpm_id else None
        effective_viewmode = DAILYPLAN_VIEWMODE_PERSONAL_DETAIL

    else:
        dailyplan = get_dailyplan_for_user(user, dailyplan_id)
        dailyplan_meals = list(dailyplan.meals_with_foods())

    detail_content_data = build_dailyplan_detail_content_data(
        dailyplan=dailyplan,
        dailyplan_meals=dailyplan_meals,
        user=user,
        viewmode=effective_viewmode,
        header_builder=build_dailyplan_header,
    )

    return DailyPlanDetailPageData(
        dailyplan=dailyplan,
        dailyplan_meals=dailyplan_meals,
        detail_content_data=detail_content_data,
        selected_meal_id=selected_meal_id,
        editing_dailyplanmeal_id=editing_dailyplanmeal_id,
        meal_picker_data_json=meal_picker_data_json,
        meal_picker_context_json=meal_picker_context_json,
        viewmode=effective_viewmode,
    )


def build_dailyplan_detail_content_data(
    dailyplan,
    dailyplan_meals,
    user,
    viewmode,
    header_builder,
):
    header = header_builder(
        dailyplan=dailyplan,
        user=user,
        viewmode=viewmode,
    )

    dp_total_kcal = dailyplan.total_kcal
    dp_protein = dailyplan.protein
    dp_carbs = dailyplan.carbs
    dp_fat = dailyplan.fat
    dp_alloc = dailyplan.alloc

    foods_aggregation = build_dailyplan_foods_aggregation(dailyplan_meals)

    structural_indicators = {
        "meals_count": len(dailyplan_meals),
        "foods_count": len(foods_aggregation),
    }

    ppk_dailyplan = get_ppk_dailyplan(dailyplan, user)

    dailyplan_meals_table_items = [
        build_dailyplanmeal_table_item(dpm)
        for dpm in dailyplan_meals
    ]

    menu = build_dailyplan_menu(dailyplan_meals)
    has_dpm = len(dailyplan_meals) > 0

    main_card_data = {
        "main_id": dailyplan.id,
        "title": {
            "name": dailyplan.name,
            "label": "DailyPlan",
            "category": dailyplan.category,
            "category_badge": resolve_category_badge(dailyplan.category),
            "icon": CONTENT_ICON_REGISTRY.get("dailyplan"),
            "meals_count": len(dailyplan_meals),
            "foods_count": structural_indicators["foods_count"],
        },
        "kpis": {
            "ppk": ppk_dailyplan["ppk"],
            "tot_kcal": dp_total_kcal,
            "g_protein": dp_protein,
            "g_carbs": dp_carbs,
            "g_fat": dp_fat,
            "kcal_protein": dailyplan.kcal_protein,
            "kcal_carbs": dailyplan.kcal_carbs,
            "kcal_fat": dailyplan.kcal_fat,
            "alloc_protein": dp_alloc["protein"],
            "alloc_carbs": dp_alloc["carbs"],
            "alloc_fat": dp_alloc["fat"],
        },
        "table_items": dailyplan_meals_table_items,
        "menu": menu,
        "metadata": {
            "owner": str(dailyplan.created_by),
            "author": str(dailyplan.original_author),
            "fork_from": str(dailyplan.forked_from) if dailyplan.forked_from else None,
        },
        "show_kpis": has_dpm,
        "show_table": has_dpm,
    }

    child_cards_data = []

    for dpm in dailyplan_meals:
        meal = dpm.meal

        meal_total_kcal = meal.total_kcal_cached or meal.total_kcal
        meal_protein = meal.protein_cached or meal.protein
        meal_carbs = meal.carbs_cached or meal.carbs
        meal_fat = meal.fat_cached or meal.fat

        meal_alloc = {
            "protein": meal.alloc_protein_cached or meal.alloc["protein"],
            "carbs": meal.alloc_carbs_cached or meal.alloc["carbs"],
            "fat": meal.alloc_fat_cached or meal.alloc["fat"],
        }

        ppk_meal = get_ppk_meal(meal, user)

        meal_foods = list(meal.meal_food_set.all())
        meal_foods_aggregation = build_meal_foods_aggregation(meal)

        meal_foods_table_items = [
            build_mealfood_table_item(mf)
            for mf in meal_foods
        ]

        child_cards_data.append(
            {
                "main_id": dailyplan.id,
                "child_id": meal.id,
                "foods_aggregation": meal_foods_aggregation,
                "related_data": {
                    "rel_id": dpm.id,
                    "hour": str(dpm.hour) if dpm.hour else None,
                    "note": dpm.note,
                    "alloc_protein": meal_alloc["protein"],
                    "alloc_carbs": meal_alloc["carbs"],
                    "alloc_fat": meal_alloc["fat"],
                },
                "title": {
                    "name": meal.name,
                    "label": "Meal",
                    "icon": CONTENT_ICON_REGISTRY.get("meal"),
                    "category": meal.category,
                    "category_badge": resolve_category_badge(meal.category),
                    "foods_count": len(meal_foods_aggregation),
                },
                "kpis": {
                    "ppk": ppk_meal["ppk"],
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
                "table_items": meal_foods_table_items,
                "metadata": {
                    "owner": str(meal.created_by),
                    "author": str(meal.original_author),
                    "fork_from": str(meal.forked_from) if meal.forked_from else None,
                },
                "actions": resolve_dailyplan_meal_actions(
                    dpm,
                    user,
                    viewmode,
                ),
            }
        )

    return DailyPlanDetailContentData(
        header=header,
        main_card_data=main_card_data,
        child_cards_data=child_cards_data,
        foods_aggregation=foods_aggregation,
        structural_indicators=structural_indicators,
    )


def get_dailyplan_list_page_data(user) -> DailyPlanListPageData:
    dailyplans = (
        dailyplans_with_kcal()
        .filter(
            created_by=user,
            is_draft=False,
        )
        .order_by("-created_at")
    )

    viewmode = DAILYPLAN_VIEWMODE_PERSONAL_LIST

    list_content_data = build_dailyplan_list_content_data(
        dailyplans=dailyplans,
        user=user,
        viewmode=viewmode,
    )

    page_actions = resolve_dailyplan_page_actions(
        user,
        viewmode,
    )

    return DailyPlanListPageData(
        dailyplans=dailyplans,
        list_content_data=list_content_data,
        page_actions=page_actions,
        viewmode=viewmode,
    )


def get_dailyplan_explore_list_page_data(user) -> DailyPlanListPageData:
    dailyplans = (
        dailyplans_with_kcal()
        .filter(
            is_public=True,
            is_draft=False,
        )
        .order_by("-created_at")
    )

    viewmode = DAILYPLAN_VIEWMODE_EXPLORE_LIST

    list_content_data = build_dailyplan_list_content_data(
        dailyplans=dailyplans,
        user=user,
        viewmode=viewmode,
    )

    page_actions = resolve_dailyplan_page_actions(
        user,
        viewmode,
    )

    return DailyPlanListPageData(
        dailyplans=dailyplans,
        list_content_data=list_content_data,
        page_actions=page_actions,
        viewmode=viewmode,
    )


def get_dailyplan_shared_list_page_data(user) -> DailyPlanListPageData:
    dailyplans = (
        dailyplans_with_kcal()
        .filter(
            shares__accepted_by=user,
            shares__removed=False,
            is_draft=False,
        )
        .prefetch_related("shares")
        .distinct()
    )

    viewmode = DAILYPLAN_VIEWMODE_SHARED_LIST

    list_content_data = build_dailyplan_list_content_data(
        dailyplans=dailyplans,
        user=user,
        viewmode=viewmode,
    )

    page_actions = resolve_dailyplan_page_actions(
        user,
        viewmode,
    )

    return DailyPlanListPageData(
        dailyplans=dailyplans,
        list_content_data=list_content_data,
        page_actions=page_actions,
        viewmode=viewmode,
    )


def get_dailyplan_draft_list_page_data(user) -> DailyPlanListPageData:
    dailyplans = (
        dailyplans_with_kcal()
        .filter(
            created_by=user,
            is_draft=True,
        )
        .order_by("-created_at")
    )

    viewmode = DAILYPLAN_VIEWMODE_DRAFT_LIST

    list_content_data = build_dailyplan_list_content_data(
        dailyplans=dailyplans,
        user=user,
        viewmode=viewmode,
    )

    page_actions = resolve_dailyplan_page_actions(
        user,
        viewmode,
    )

    return DailyPlanListPageData(
        dailyplans=dailyplans,
        list_content_data=list_content_data,
        page_actions=page_actions,
        viewmode=viewmode,
    )


def build_dailyplan_list_content_data(dailyplans, user, viewmode):
    child_cards_data = []

    for dailyplan in dailyplans:
        dp_total_kcal = dailyplan.total_kcal
        dp_protein = dailyplan.protein
        dp_carbs = dailyplan.carbs
        dp_fat = dailyplan.fat

        dp_kcal_protein = dailyplan.kcal_protein
        dp_kcal_carbs = dailyplan.kcal_carbs
        dp_kcal_fat = dailyplan.kcal_fat

        dp_alloc = dailyplan.alloc

        ppk = get_ppk_dailyplan(dailyplan, user)

        dailyplan_meals = list(dailyplan.meals_with_foods())

        dailyplan_meals_table_items = [
            build_dailyplanmeal_table_item(dpm)
            for dpm in dailyplan_meals
        ]

        menu = build_dailyplan_menu(dailyplan_meals)
        foods_aggregation = build_dailyplan_foods_aggregation(dailyplan_meals)

        share = next(
            (
                s for s in dailyplan.shares.all()
                if s.accepted_by_id == user.id and not s.removed
            ),
            None
        )

        actions = []

        actions.extend(
            resolve_dailyplan_entity_actions(
                dailyplan,
                user,
                viewmode,
            )
        )

        if share:
            actions.extend(
                resolve_share_actions(
                    share,
                    user,
                    viewmode,
                )
            )

        child_cards_data.append(
            {
                "child_id": dailyplan.id,
                "title": {
                    "name": dailyplan.name,
                    "label": "DailyPlan",
                    "icon": CONTENT_ICON_REGISTRY.get("dailyplan"),
                    "category": dailyplan.category,
                    "category_badge": resolve_category_badge(dailyplan.category),
                    "meals_count": len(dailyplan_meals),
                    "foods_count": len(foods_aggregation),
                },
                "kpis": {
                    "ppk": ppk["ppk"],
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
                "table_items": dailyplan_meals_table_items,
                "menu": menu,
                "foods_aggregation": foods_aggregation,
                "metadata": {
                    "owner": str(dailyplan.created_by),
                    "author": str(dailyplan.original_author),
                    "fork_from": str(dailyplan.forked_from) if dailyplan.forked_from else None,
                },
                "actions": actions,
                "if_shared": {
                    "child_id": dailyplan.id,
                    "share_id": share.id if share else None,
                },
            }
        )

    return DailyPlanListContentData(
        child_cards_data=child_cards_data,
    )