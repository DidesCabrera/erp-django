from notas.viewmodels.content.edit_food_vm import *


def build_food_edit_vm(food):
    
    return FoodEditVM(
        id=food.id,
        name=food.name,
        protein=food.protein,
        carbs=food.carbs,
        fat=food.fat,
    )