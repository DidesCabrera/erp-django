from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from notas.presentation.config.viewmodel_config import PROFILE_VIEWMODE
from notas.presentation.viewmodels.base_vm import BaseVM
from notas.presentation.viewmodels.ui.builder_ui import build_ui_vm


@login_required
def profile_detail(request):
    profile = request.user.profile

    ui = build_ui_vm(PROFILE_VIEWMODE)

    vm = BaseVM(
        ui=ui,
        content=None,
    )

    context = vm.as_context()
    context["profile"] = profile

    return render(
        request,
        "notas/profile/detail.html",
        context,
    )