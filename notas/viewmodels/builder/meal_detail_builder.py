from notas.services.kpis import get_ppk_meal
from notas.actions.meal_food_resolvers import resolve_food_actions
from notas.viewmodels.meal_detail_vm import *
from notas.viewmodels.builder.builder_table_items import build_mealfood_table_item
from notas.viewmodels.builder.builder_headers import build_meal_header


def build_meal_detail_vm(meal, user, action_context):

    # ==================================================
    # HEADER
    # ==================================================

    header = build_meal_header(
        meal=meal,
        user=user,
        context_name=action_context
    )

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

    # ==================================================
    # MAIN CARD
    # ==================================================

    ppk = get_ppk_meal(meal, user)

    meal_foods = list(meal.meal_food_set.all())

    meal_foods_table_items = [
        build_mealfood_table_item(mf)
        for mf in meal_foods
    ]

    has_mf = len(meal_foods) > 0

    main = MainCardUI(
        main_id=meal.id,

        titulo=TitleUI(
            name=meal.name,
            label="Meal"
        ),

        kpis=KPIUI(
            ppk=ppk["ppk"],
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

        show_kpis=has_mf,
        show_table=has_mf,

        metadata=MetadataUI(
            owner=str(meal.created_by),
            author=str(meal.original_author),
            fork_from=str(meal.forked_from) if meal.forked_from else None,
        )
    )

    # ==================================================
    # CHILD CARDS (FOODS)
    # ==================================================

    children = []

    for mf in meal_foods:

        food = mf.food

        # --- freeze food aggregates (food is per 100g) ---
        food_total_kcal = food.total_kcal
        food_protein = food.protein
        food_carbs = food.carbs
        food_fat = food.fat

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
                ppk=ppk["ppk"],
                tot_kcal=food_total_kcal,

                g_protein=food_protein,
                g_carbs=food_carbs,
                g_fat=food_fat,

                kcal_protein=food.kcal_protein,
                kcal_carbs=food.kcal_carbs,
                kcal_fat=food.kcal_fat,

                alloc_protein=food_alloc["protein"],
                alloc_carbs=food_alloc["carbs"],
                alloc_fat=food_alloc["fat"],
            ),

            actions=resolve_food_actions(
                mf,
                user,
                context={"name": action_context}
            )
        )

        children.append(child)

    # ==================================================
    # FINAL VM
    # ==================================================

    return MealDetailVM(
        header=header,
        main_card=main,
        child_cards=children,
    )
