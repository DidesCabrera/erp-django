from notas.application.services.kpis import get_ppk_dailyplan
from notas.application.resolvers.dailyplan_resolvers import resolve_dailyplan_actions
from notas.application.resolvers.share_resolvers import resolve_share_actions
from notas.presentation.viewmodels.content.list_vm import *
from notas.presentation.viewmodels.content.registry import CONTENT_ICON_REGISTRY
from notas.presentation.composition.viewmodel.builder_table_items import build_dailyplanmeal_table_item
from notas.presentation.config.viewmodel_config import ALLOC_PCT_OUTSIDE_THRESHOLD

from notas.presentation.composition.viewmodel.builder_foods_aggregation import  build_dailyplan_foods_aggregation
from notas.presentation.composition.viewmodel.builder_menu import build_dailyplan_menu





def build_dailyplan_list_vm(dailyplans, user, viewmode):

    children = []

    for dailyplan in dailyplans:

        child_entity_icon = CONTENT_ICON_REGISTRY.get("dailyplan")
        child_entity_label = "DailyPlan"

        # ==================================================
        # Freeze dailyplan aggregates (single access)
        # ==================================================

        dp_total_kcal = dailyplan.total_kcal
        dp_protein = dailyplan.protein
        dp_carbs = dailyplan.carbs
        dp_fat = dailyplan.fat

        dp_kcal_protein = dailyplan.kcal_protein
        dp_kcal_carbs = dailyplan.kcal_carbs
        dp_kcal_fat = dailyplan.kcal_fat

        dp_alloc = dailyplan.alloc

        # ==================================================
        # KPIs
        # ==================================================

        ppk = get_ppk_dailyplan(dailyplan, user)

        # ==================================================
        # Meals + aggregations
        # ==================================================

        dailyplan_meals = dailyplan.meals_with_foods()

        dailyplan_meals_table_items = [
            build_dailyplanmeal_table_item(dpm)
            for dpm in dailyplan_meals
        ]
        
        menu = build_dailyplan_menu(dailyplan_meals)
        foods_aggregation = build_dailyplan_foods_aggregation(dailyplan_meals)


        # ==================================================
        # Actions & Share (if exists)
        # ==================================================

        share = next(
            (
                s for s in dailyplan.shares.all()
                if s.accepted_by_id == user.id and not s.removed
            ),
            None
        )

        actions = []

        actions.extend(
            resolve_dailyplan_actions(
                dailyplan,
                user,
                context={"name": viewmode}
            )
        )

        if share:
            actions.extend(
                resolve_share_actions(
                    share,
                    user,
                    context={"name": viewmode}
                )
            )

        # ==================================================
        # Completar Child card con la información respectiva
        # ==================================================

        child = ChildCardUI(
            child_id=dailyplan.id,

            titulo=TitleUI(
                name=dailyplan.name,
                label= child_entity_label,
                icon= child_entity_icon,
                category=dailyplan.category,
                structural_indicators=StructuralIndicatorsUI(
                    meals_count=len(dailyplan_meals),
                    foods_count=len(foods_aggregation),
                )
            ),

            kpis=KPIUI(
                ppk=ppk["ppk"],
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

                pct_outside_protein=dp_alloc["protein"] < ALLOC_PCT_OUTSIDE_THRESHOLD,
                pct_outside_carbs=dp_alloc["carbs"] < ALLOC_PCT_OUTSIDE_THRESHOLD,
                pct_outside_fat=dp_alloc["fat"] < ALLOC_PCT_OUTSIDE_THRESHOLD,
            ),

            table={"items": dailyplan_meals_table_items},

            menu=menu,

            foods_aggregation=foods_aggregation,

            metadata=MetadataUI(
                owner=str(dailyplan.created_by),
                author=str(dailyplan.original_author),
                fork_from=str(dailyplan.forked_from) if dailyplan.forked_from else None,
            ),

            actions=actions,

            if_shared=IfShared(
                child_id=dailyplan.id,
                share_id=share.id if share else None
            )
        )

        children.append(child)

    return ListVM(
        child_cards=children,
    )
