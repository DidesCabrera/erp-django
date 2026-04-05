
def build_dailyplan_detail_vm(dailyplan, dailyplan_meals, user, viewmode):

    # ==================================================
    # HEADER
    # ==================================================

    header = build_dailyplan_header(
        dailyplan=dailyplan,
        user=user,
        viewmode=viewmode
    )
    
    main_entity_icon = CONTENT_ICON_REGISTRY.get("dailyplan")
    main_entity_label = "DailyPlan"

    # ==================================================
    # DAILYPLAN AGGREGATES (freeze values)
    # ==================================================

    dp_total_kcal = dailyplan.total_kcal
    dp_protein = dailyplan.protein
    dp_carbs = dailyplan.carbs
    dp_fat = dailyplan.fat

    dp_alloc = dailyplan.alloc

    foods_aggregation = build_dailyplan_foods_aggregation(dailyplan_meals)

    structural_indicators = StructuralIndicatorsUI(
        meals_count=len(dailyplan_meals),
        foods_count=len(foods_aggregation),
    )

    # ==================================================
    # MAIN CARD
    # ==================================================

    ppk = get_ppk_dailyplan(dailyplan, user)

    dailyplan_meals_table_items = [
        build_dailyplanmeal_table_item(dpm)
        for dpm in dailyplan_meals
    ]

    has_dpm = len(dailyplan_meals) > 0

    main = MainCardUI(
        main_id=dailyplan.id,

        titulo=TitleUI(
            name=dailyplan.name,
            label= main_entity_label,
            category=dailyplan.category,
            icon= main_entity_icon,
        ),

        kpis=KPIUI(
            ppk=ppk["ppk"],
            tot_kcal=dp_total_kcal,

            g_protein=dp_protein,
            g_carbs=dp_carbs,
            g_fat=dp_fat,

            kcal_protein=dailyplan.kcal_protein,
            kcal_carbs=dailyplan.kcal_carbs,
            kcal_fat=dailyplan.kcal_fat,

            alloc_protein=dp_alloc["protein"],
            alloc_carbs=dp_alloc["carbs"],
            alloc_fat=dp_alloc["fat"],
        ),

        table={"items": dailyplan_meals_table_items},

        metadata=MetadataUI(
            owner=str(dailyplan.created_by),
            author=str(dailyplan.original_author),
            fork_from=str(dailyplan.forked_from) if dailyplan.forked_from else None,
        ),
        
        show_kpis=has_dpm,
        show_table=has_dpm,
    )

    # ==================================================
    # CHILD CARDS (MEALS)
    # ==================================================

    children = []

    for dpm in dailyplan_meals:

        meal = dpm.meal

        # --- freeze meal aggregates (cached if available) ---
        meal_total_kcal = meal.total_kcal_cached or meal.total_kcal
        meal_protein = meal.protein_cached or meal.protein
        meal_carbs = meal.carbs_cached or meal.carbs
        meal_fat = meal.fat_cached or meal.fat

        meal_alloc = {
            "protein": meal.alloc_protein_cached or meal.alloc["protein"],
            "carbs": meal.alloc_carbs_cached or meal.alloc["carbs"],
            "fat": meal.alloc_fat_cached or meal.alloc["fat"],
        }

        # --- ppk ---
        ppk = get_ppk_meal(meal, user)

        # --- foods ---
        meal_foods = list(meal.meal_food_set.all())
        meal_foods_aggregation = build_meal_foods_aggregation(meal)

        meal_foods_table_items = [
            build_mealfood_table_item(mf)
            for mf in meal_foods
        ]

        child_entity_icon = CONTENT_ICON_REGISTRY.get("meal")
        child_entity_label = "Meal"

        child = ChildCardUI(

            main_id=dailyplan.id,
            child_id=meal.id,

            foods_aggregation=meal_foods_aggregation,

            related_data=DpmRelatedDataUI(
                rel_id=dpm.id,
                hour=str(dpm.hour) if dpm.hour else None,
                note=dpm.note,
                alloc_protein=meal_alloc["protein"],
                alloc_carbs=meal_alloc["carbs"],
                alloc_fat=meal_alloc["fat"],
            ),

            titulo=TitleUI(
                name=meal.name,
                label= child_entity_label,
                icon= child_entity_icon,
                category=meal.category,
                structural_indicators=StructuralIndicatorsUI(
                    foods_count=len(meal_foods_aggregation),
                )
            ),

            kpis=KPIUI(
                ppk=ppk["ppk"],
                tot_kcal=meal_total_kcal,

                g_protein=meal_protein,
                g_carbs=meal_carbs,
                g_fat=meal_fat,

                kcal_protein=meal.kcal_protein_cached or meal.kcal_protein,
                kcal_carbs=meal.kcal_carbs_cached or meal.kcal_carbs,
                kcal_fat=meal.kcal_fat_cached or meal.kcal_fat,

                alloc_protein=meal_alloc["protein"],
                alloc_carbs=meal_alloc["carbs"],
                alloc_fat=meal_alloc["fat"],
            ),

            table={"items": meal_foods_table_items},

            metadata=MetadataUI(
                owner=str(meal.created_by),
                author=str(meal.original_author),
                fork_from=str(meal.forked_from) if meal.forked_from else None,
            ),

            actions=resolve_dailyplan_meal_actions(
                dpm,
                user,
                viewmode
            )
        )

        children.append(child)

    # ==================================================
    # FINAL VM
    # ==================================================

    return DailyPlanDetailVM(
        header=header,
        main_card=main,
        child_cards=children,
        foods_aggregation=foods_aggregation,
        structural_indicators=structural_indicators,
    )


