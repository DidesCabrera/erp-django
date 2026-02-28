from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notas.viewmodels.builder.nutrition_builder import build_elemental_view_vm

@login_required
def elemental_context(request):
    
    vm = build_elemental_view_vm(request.user)

    return render(
        request,
        "notas/elementals/context.html",
        vm.as_context(),
    )

def elemental_nutrition(request):
    
    vm = build_elemental_view_vm(request.user)

    return render(
        request,
        "notas/elementals/nutrition.html",
        vm.as_context(),
    )

def elemental_platform(request):
    
    vm = build_elemental_view_vm(request.user)

    return render(
        request,
        "notas/elementals/platform.html",
        vm.as_context(),
    )
