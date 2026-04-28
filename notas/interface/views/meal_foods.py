from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction

from notas.domain.models import MealFood, Meal, Food



#************ RENDER COMPLEJOS *********************
# ---------- DETAIL (NO HAY LIST)  ----------

@login_required
@require_POST
def mealfood_update(request, meal_id, mealfood_id):

    meal = get_object_or_404(
        Meal,
        id=meal_id,
        created_by=request.user,
    )

    mealfood = get_object_or_404(
        MealFood.objects.select_related("meal"),
        id=mealfood_id,
        meal=meal,
    )

    return_to = (
        request.POST.get("return_to")
        or request.GET.get("return_to")
    )

    try:
        quantity = float(request.POST.get("quantity", 0))
    except ValueError:
        quantity = 0

    if quantity <= 0:
        messages.error(request, "La cantidad debe ser mayor a 0.")
        if return_to:
            return redirect(return_to)
        return redirect("meal_detail", meal.id)

    mealfood.quantity = quantity
    
    food_id = request.POST.get("food_id")

    if food_id:
        mealfood.food_id = int(food_id)


    mealfood.save()

    messages.success(request, "Alimento actualizado correctamente.")

    if return_to:
        return redirect(return_to)

    return redirect("meal_detail", pk=meal.pk)


@login_required
@require_POST
def mealfood_remove(request, pk):

    mf = get_object_or_404(
        MealFood.objects.select_related("meal", "meal__created_by"),
        pk=pk,
        meal__created_by=request.user,
    )

    meal = mf.meal

    # 🔑 NUEVO: destino explícito
    return_to = (
        request.POST.get("return_to")
        or request.GET.get("return_to")
    )

    mf.delete()

    # 👉 prioridad absoluta: return_to
    if return_to:
        return redirect(return_to)

    return redirect("meal_detail", pk=meal.pk)


@require_POST
def add_food_to_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk)

    food_id = request.POST.get("food_id")
    quantity = request.POST.get("quantity")

    # 🔑 NUEVO: destino explícito (POST o GET)
    return_to = (
        request.POST.get("return_to")
        or request.GET.get("return_to")
    )

    if not food_id or not quantity:
        messages.error(request, "Food y cantidad son obligatorios")

        # 👉 prioridad absoluta: return_to
        if return_to:
            return redirect(return_to)

        return redirect("meal_detail", pk=meal.pk)

    food = get_object_or_404(Food, pk=food_id)

    next_order = meal.meal_food_set.count() + 1

    MealFood.objects.create(
        meal=meal,
        food=food,
        quantity=quantity,
        order=next_order,
    )
    meal.update_draft_status()

    messages.success(request, "Food agregado a la meal")

    # 👉 prioridad absoluta: return_to
    if return_to:
        return redirect(return_to)

    return redirect("meal_detail", pk=meal.pk)

@login_required
@require_POST
@transaction.atomic
def mealfood_reorder(request, meal_id):
    meal = get_object_or_404(
        Meal,
        id=meal_id,
        created_by=request.user,
    )

    ordered_ids = request.POST.getlist("mealfood_order[]")

    if not ordered_ids:
        return JsonResponse(
            {"ok": False, "error": "Missing order payload"},
            status=400,
        )

    meal_foods = list(
        MealFood.objects.filter(
            meal=meal,
            id__in=ordered_ids,
        )
    )

    meal_food_by_id = {
        str(meal_food.id): meal_food
        for meal_food in meal_foods
    }

    if len(meal_food_by_id) != len(ordered_ids):
        return JsonResponse(
            {"ok": False, "error": "Invalid MealFood ids"},
            status=400,
        )

    for index, mealfood_id in enumerate(ordered_ids, start=1):
        meal_food = meal_food_by_id[str(mealfood_id)]
        meal_food.order = index
        meal_food.save(update_fields=["order"])

    return JsonResponse({"ok": True})
