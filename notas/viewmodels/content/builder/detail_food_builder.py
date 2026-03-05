from notas.services.kpis import get_ppk_meal
from notas.actions.food_resolvers import resolve_food_actions
from notas.viewmodels.content.detail_food_vm import *
from notas.viewmodels.content.builder.builder_headers import build_food_header

from notas.viewmodels.content.registry import CONTENT_ICON_REGISTRY


def build_food_detail_vm(food, user, action_context):

    main_entity_icon = CONTENT_ICON_REGISTRY.get("food")
    main_entity_label = "Food"

    # ==================================================
    # HEADER
    # ==================================================

    header = build_food_header(
        food=food,
        user=user,
        context_name=action_context
    )

    # ==================================================
    # Freeze MEAL aggregates (cached if available)
    # ==================================================

    food_total_kcal = food.total_kcal
    food_protein = food.protein
    food_carbs = food.carbs
    food_fat = food.fat

    food_kcal_protein = food.kcal_protein
    food_kcal_carbs = food.kcal_carbs
    food_kcal_fat = food.kcal_fat

    food_alloc = {
        "protein": food.alloc["protein"],
        "carbs": food.alloc["carbs"],
        "fat": food.alloc["fat"],
    }

    # ==================================================
    # MAIN CARD
    # ==================================================


    main = MainCardUI(
        main_id=food.id,

        titulo=TitleUI(
            name=food.name,
            label= main_entity_label,
            icon= main_entity_icon,
        ),

        kpis=KPIUI(
            tot_kcal=food_total_kcal,

            g_protein=food_protein,
            g_carbs=food_carbs,
            g_fat=food_fat,

            kcal_protein=food_kcal_protein,
            kcal_carbs=food_kcal_carbs,
            kcal_fat=food_kcal_fat,

            alloc_protein=food_alloc["protein"],
            alloc_carbs=food_alloc["carbs"],
            alloc_fat=food_alloc["fat"],
        )
    )

    return FoodDetailVM(
        header=header,
        main_card=main,
    )
