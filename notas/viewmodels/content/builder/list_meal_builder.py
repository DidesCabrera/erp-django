from notas.services.kpis import get_ppk_meal
from notas.actions.meal_resolvers import resolve_meal_actions
from notas.actions.share_resolvers import resolve_share_actions
from notas.viewmodels.content.list_vm import *
from notas.viewmodels.content.builder.builder_table_items import build_mealfood_table_item
from notas.viewmodels.content.builder.builder_foods_aggregation import build_meal_foods_aggregation
from notas.viewmodels.content.registry import CONTENT_ICON_REGISTRY


def build_meal_list_vm(meals, user, action_context):
    
    children = []

    for meal in meals:

        child_entity_icon = CONTENT_ICON_REGISTRY.get("meal")
        child_entity_label = "Meal"

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
        # KPIs
        # ==================================================

        ppk = get_ppk_meal(meal, user)

        # ==================================================
        # Foods (materialize once)
        # ==================================================

        meal_foods = list(meal.meal_food_set.all())

        meal_foods_table_items = [
            build_mealfood_table_item(mf)
            for mf in meal_foods
        ]

        foods_aggregation = build_meal_foods_aggregation(meal)

        # ==================================================
        # Share (if exists)
        # ==================================================

        share = next(
            (
                s for s in meal.shares.all()
                if s.accepted_by_id == user.id and not s.removed
            ),
            None
        )

        # ==================================================
        # Actions
        # ==================================================

        actions = []

        actions.extend(
            resolve_meal_actions(
                meal,
                user,
                context={"name": action_context}
            )
        )

        if share:
            actions.extend(
                resolve_share_actions(
                    share,
                    user,
                    context={"name": action_context}
                )
            )

        # ==================================================
        # Child card
        # ==================================================

        child = ChildCardUI(
            child_id=meal.id,

            titulo=TitleUI(
                name=meal.name,
                label= child_entity_label,
                icon= child_entity_icon,
                category=meal.category,
                structural_indicators=StructuralIndicatorsUI(
                    foods_count=len(foods_aggregation),
                )
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

            foods_aggregation=foods_aggregation,

            metadata=MetadataUI(
                owner=str(meal.created_by),
                author=str(meal.original_author),
                fork_from=str(meal.forked_from) if meal.forked_from else None,
            ),

            actions=actions,

            if_shared=IfShared(
                child_id=meal.id,
                share_id=share.id if share else None
            )
        )

        children.append(child)

    return ListVM(
        child_cards=children,
    )
