from datetime import date
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from notas.models import WeightLog

@login_required
def register_weight(request):
    back_url = request.META.get("HTTP_REFERER", "meal_list")

    if request.method != "POST":
        return redirect(back_url)

    try:
        weight = float(request.POST.get("weight", 0))
    except (TypeError, ValueError):
        messages.error(request, "Ingresa un número válido.")
        return redirect(back_url)

    if weight <= 0:
        messages.error(request, "El peso debe ser mayor a 0.")
        return redirect(back_url)

    WeightLog.objects.update_or_create(
        user=request.user,
        date=date.today(),
        defaults={"weight_kg": weight},
    )

    messages.success(request, "Peso registrado correctamente.")
    return redirect(back_url)
