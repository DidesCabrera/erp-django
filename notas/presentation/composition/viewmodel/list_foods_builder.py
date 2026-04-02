from notas.presentation.viewmodels.content.list_food_vm import FoodListVM, FoodListItemVM
from notas.interface.routing.food import food_url
from notas.application.resolvers.food_resolvers import resolve_food_actions

def build_food_list_vm(foods, user, viewmode):

    items = []

    for food in foods:
        items.append(
            FoodListItemVM(
                id=food.id,
                name=food.name,
                protein=food.protein,
                carbs=food.carbs,
                fat=food.fat,
                total_kcal=food.total_kcal,
                alloc=food.alloc,
                url=food_url(food),
                actions=resolve_food_actions(
                    food,
                    user,
                    viewmode
                ),
            )
        )

    return FoodListVM(items=items)