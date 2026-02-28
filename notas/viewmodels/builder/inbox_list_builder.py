from notas.viewmodels.list_vm import *
from notas.viewmodels.builder.builder_headers import build_list_header



def build_inbox_list_vm(user):

    # =========================
    # HEADER
    # =========================

    header = build_list_header(
        entity="inbox",
        context_name="inbox"
    )

    children = []

    return ListVM(
        header=header,
        child_cards=children,
    )
