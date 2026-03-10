from notas.forms.builder.form_food_builder import build_form_fields
from notas.viewmodels.content.edit_food_vm import EditFoodVM

def build_edit_food_vm(food):

    return EditFoodVM(
        food=food
    )