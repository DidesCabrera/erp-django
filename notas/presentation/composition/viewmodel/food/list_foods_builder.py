from notas.presentation.viewmodels.content.food.list_food_vm import *
from notas.presentation.config.viewmodel_config import ALLOC_PCT_OUTSIDE_THRESHOLD
from notas.presentation.composition.viewmodel.components.builder_headers import build_page_header
from notas.application.resolvers.food_resolvers import resolve_food_entity_actions
from notas.presentation.config.icons import CONTENT_ICON_REGISTRY
from notas.presentation.resolvers.title_resolvers import resolve_category_badge


def build_food_list_vm(foods, user, viewmode, page_actions=None):
    items = []

    for food in foods:
        ppk = 0

        alloc = food.alloc

        item = ItemUI(
            child_id=food.id,

            titulo=TitleUI(
                name=food.name,
                label="Food",
                icon=CONTENT_ICON_REGISTRY.get("food"),
                category=getattr(food, "category", None),
                category_badge=resolve_category_badge(getattr(food, "category", None)),
            ),

            kpis=KPIUI(
                ppk=ppk,
                tot_kcal=float(food.total_kcal),
                g_protein=float(food.protein),
                g_carbs=float(food.carbs),
                g_fat=float(food.fat),
                kcal_protein=float(food.protein) * 4,
                kcal_carbs=float(food.carbs) * 4,
                kcal_fat=float(food.fat) * 9,
                alloc_protein=float(alloc["protein"]),
                alloc_carbs=float(alloc["carbs"]),
                alloc_fat=float(alloc["fat"]),
                pct_outside_protein=(
                    float(alloc["protein"]) < ALLOC_PCT_OUTSIDE_THRESHOLD
                ),
                pct_outside_carbs=(
                    float(alloc["carbs"]) < ALLOC_PCT_OUTSIDE_THRESHOLD
                ),
                pct_outside_fat=(
                    float(alloc["fat"]) < ALLOC_PCT_OUTSIDE_THRESHOLD
                ),
            ),

            metadata=MetadataUI(
                owner=str(food.created_by),
                author=str(getattr(food, "original_author", "")),
                fork_from=str(food.forked_from) if getattr(food, "forked_from", None) else None,
            ),

            actions=resolve_food_entity_actions(
                food,
                user,
                viewmode,
            ),
        )

        items.append(item)

    return FoodListVM(
        header=build_page_header(actions=page_actions or []),
        items=items,
    )