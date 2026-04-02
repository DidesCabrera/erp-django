from notas.application.services.kpis import (
    get_ppk_dailyplan,
    get_ppk_meal,
)

from notas.application.resolvers.meal_food_resolvers import resolve_meal_food_actions

from notas.presentation.viewmodels.content.dpm.detail_dpm_vm import *
from notas.presentation.config.icons import CONTENT_ICON_REGISTRY

from notas.presentation.composition.viewmodel.components.builder_table_items import build_mealfood_table_item
from notas.presentation.composition.viewmodel.components.builder_headers import build_dailyplan_meal_header





def build_dpm_detail_vm(dailyplan, dpm, user, viewmode):

    main_entity_icon = CONTENT_ICON_REGISTRY.get("meal")
    main_entity_label = "Meal"

    # ==================================================
    # HEADER
    # ==================================================

    header = build_dailyplan_meal_header(
        dpm=dpm,
        user=user,
        viewmode=viewmode
    )

    # ==================================================
    # Freeze DAILYPLAN aggregates
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

    meal = dpm.meal

    # ==================================================
    # Freeze MEAL aggregates (cached if available)
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

    # ==================================================
    # FATHER CARD (DailyPlan)
    # ==================================================

    father = FatherCardUI(
        father_id=dailyplan.id,

        titulo=TitleUI(
            name=dailyplan.name,
            label= "Daily Plan",
            category=dailyplan.category,
        ),

        rel_id=dpm.id,

        kpis=KPIUI(
            ppk=father_ppk["ppk"],
            tot_kcal=dp_total_kcal,

            g_protein=dp_protein,
            g_carbs=dp_carbs,
            g_fat=dp_fat,

            kcal_protein=dp_kcal_protein,
            kcal_carbs=dp_kcal_carbs,
            kcal_fat=dp_kcal_fat,

            alloc_protein=dp_alloc["protein"],
            alloc_carbs=dp_alloc["carbs"],
            alloc_fat=dp_alloc["fat"],
        ),

        related_data=DpmRelatedDataUI(
            rel_id=dpm.id,
            hour=str(dpm.hour) if dpm.hour else None,
            note=dpm.note,
            alloc_protein=meal_alloc["protein"],
            alloc_carbs=meal_alloc["carbs"],
            alloc_fat=meal_alloc["fat"],
        ),
    )

    # ==================================================
    # MAIN CARD (Meal)
    # ==================================================

    meal_foods = list(meal.meal_food_set.all())

    meal_foods_table_items = [
        build_mealfood_table_item(mf)
        for mf in meal_foods
    ]

    main = MainCardUI(
        main_id=meal.id,

        titulo=TitleUI(
            name=meal.name,
            label= main_entity_label,
            icon= main_entity_icon,
            category=meal.category,
        ),

        kpis=KPIUI(
            ppk=meal_ppk["ppk"],
            tot_kcal=meal_total_kcal,

            g_protein=meal_protein,
            g_carbs=meal_carbs,
            g_fat=meal_fat,

            kcal_protein=meal_kcal_protein,
            kcal_carbs=meal_kcal_carbs,
            kcal_fat=meal_kcal_fat,

            alloc_protein=meal_alloc["protein"],
            alloc_carbs=meal_alloc["carbs"],
            alloc_fat=meal_alloc["fat"],
        ),

        table={"items": meal_foods_table_items},

        metadata=MetadataUI(
            owner=str(meal.created_by),
            author=str(meal.original_author),
            fork_from=str(meal.forked_from) if meal.forked_from else None,
        )
    )

    # ==================================================
    # CHILD CARDS (Foods)
    # ==================================================

    children = []

    for mf in meal_foods:

        food = mf.food

        # food values are per 100g → no cache needed
        food_alloc = food.alloc

        child = ChildCardUI(
            child_id=food.id,

            related_data=MfRelatedDataUI(
                rel_id=mf.id,
                quantity=mf.quantity,
                alloc_protein=food_alloc["protein"],
                alloc_carbs=food_alloc["carbs"],
                alloc_fat=food_alloc["fat"],
            ),

            titulo=TitleUI(
                name=food.name,
                label="Food"
            ),

            kpis=KPIUI(
                ppk=meal_ppk["ppk"],
                tot_kcal=food.total_kcal,

                g_protein=food.protein,
                g_carbs=food.carbs,
                g_fat=food.fat,

                kcal_protein=food.kcal_protein,
                kcal_carbs=food.kcal_carbs,
                kcal_fat=food.kcal_fat,

                alloc_protein=food_alloc["protein"],
                alloc_carbs=food_alloc["carbs"],
                alloc_fat=food_alloc["fat"],
            ),

            actions=resolve_meal_food_actions(
                mf,
                user,
                viewmode
            )
        )

        children.append(child)

    # ==================================================
    # FINAL VM
    # ==================================================

    return DpmDeepDetailVM(
        header=header,
        father_card=father,
        main_card=main,
        child_cards=children,
    )
