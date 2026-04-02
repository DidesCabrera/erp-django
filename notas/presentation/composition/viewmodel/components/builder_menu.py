from notas.presentation.viewmodels.content.dailyplan.list_vm import MenuUI, MenuMealUI


def build_dailyplan_menu(dailyplan_meals):

    meals_menu = []

    for dpm in dailyplan_meals:

        meal = dpm.meal

        foods = [
            mf.food.name
            for mf in meal.meal_food_set.all()
        ]

        meals_menu.append(
            MenuMealUI(
                meal_name=meal.name,
                foods=foods
            )
        )

    return MenuUI(meals=meals_menu)