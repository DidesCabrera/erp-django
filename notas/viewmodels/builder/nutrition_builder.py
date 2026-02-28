from notas.viewmodels.list_vm import *
from notas.viewmodels.builder.builder_headers import build_list_header



def build_elemental_view_vm(user):

    header = build_list_header(
        entity="nutrition",
        context_name="nutrition"
    )
    
    children = []

    return ListVM(
        header=header,
        child_cards=children,
    )
