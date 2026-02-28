from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notas.services.inbox import build_inbox_items
from notas.viewmodels.builder.inbox_list_builder import build_inbox_list_vm


@login_required
def inbox_list(request):

    vm = build_inbox_list_vm(
        request.user,
    )

    items = build_inbox_items(request.user)

    return render(
        request,
        "notas/inbox.html",
        {
            "items": items,
            "vm": vm
        }
    )
