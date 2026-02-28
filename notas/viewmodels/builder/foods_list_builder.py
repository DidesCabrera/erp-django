from notas.viewmodels.list_vm import *
from notas.viewmodels.builder.builder_headers import build_list_header



def build_food_list_vm(foods, user, action_context):

    # =========================
    # HEADER
    # =========================

    header = build_list_header(
        entity="food",
        context_name=action_context
    )

    children = []

    return ListVM(
        header=header,
        child_cards=children
    )
