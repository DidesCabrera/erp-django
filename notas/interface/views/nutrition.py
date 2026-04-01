from django.shortcuts import render


def elemental_context(request):
    return render(
        request,
        "notas/elementals/context.html"
    )

def elemental_nutrition(request):
    return render(
        request,
        "notas/elementals/nutrition.html",
    )

def elemental_platform(request):
    return render(
        request,
        "notas/elementals/platform.html"
    )
