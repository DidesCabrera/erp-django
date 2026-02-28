from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from notas.services.capabilities import get_capabilities
from notas.models import Meal, MealFood, DailyPlan, DailyPlanMeal, Food
from django.urls import reverse
from notas.actions.constants import (
    DAILYPLAN_MEAL_VIEWMODE_DEEP_EDIT,
    DAILYPLAN_MEAL_VIEWMODE_DETAIL,
)
from notas.viewmodels.builder.dpm_detail_builder import build_dpm_detail_vm
from notas.jscontext.builder.dpm_food_picker_builder import build_dpm_food_picker_context_payload
from notas.jscontext.builder.food_picker_builder import build_food_picker_foods_payload
from notas.services.kpis import build_nutrition_kpis_from_meal, build_nutrition_kpis_from_dailyplan
import json
from django.core.serializers.json import DjangoJSONEncoder
from notas.services.dpm import ensure_dpm_meal_isolated



#************ RENDER COMPLEJOS *********************
# ---------- DETAIL (NO HAY LIST)  ----------

#corregir
@login_required
def dailyplan_meal_detail(request, dailyplan_id, pk):

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=dailyplan_id,
        created_by=request.user,
    )

    dpm = get_object_or_404(
        DailyPlanMeal.objects
            .select_related("meal", "dailyplan")
            .prefetch_related("meal__meal_food_set__food"),
        pk=pk,
        dailyplan=dailyplan,
    )

    vm = build_dpm_detail_vm(
        dailyplan,
        dpm,
        request.user,
        DAILYPLAN_MEAL_VIEWMODE_DETAIL,
    )

    return render(
        request,
        "notas/dailyplan_meals/detail.html",
        vm.as_context(),
    )

# ---------- EDIT - DEEP EDIT ----------

@login_required
def dailyplan_meal_edit(request, dailyplan_id, dailyplanmeal_id):

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=dailyplan_id,
        created_by=request.user,
    )

    dpm = get_object_or_404(
        DailyPlanMeal.objects
            .select_related("meal", "dailyplan")
            .prefetch_related("meal__meal_food_set__food"),
        pk=dailyplanmeal_id,
        dailyplan=dailyplan,
    )

    if request.method == "POST":
        dpm.hour = request.POST.get("hour") or None
        dpm.note = request.POST.get("note") or None
        dpm.save()
        return redirect("dailyplan_edit", pk=dailyplan.id)

    vm = build_dpm_detail_vm(
        dailyplan,
        dpm,
        request.user,
        DAILYPLAN_MEAL_VIEWMODE_DEEP_EDIT,
    )

    return render(
        request,
        "notas/dailyplan_meals/edit.html",
        vm.as_context(),
    )


@login_required
def dailyplanmeal_deepedit(request, dailyplan_id, dailyplanmeal_id):

    dpm = get_object_or_404(
        DailyPlanMeal.objects
            .select_related("meal", "dailyplan")
            .prefetch_related(
                "meal__meal_food_set",
                "meal__meal_food_set__food"
            ),
        id=dailyplanmeal_id,
        dailyplan_id=dailyplan_id,
        dailyplan__created_by=request.user,
    )

    user=request.user

    meal = ensure_dpm_meal_isolated(dpm, user)
    dailyplan = dpm.dailyplan

    caps = get_capabilities(user)
    if not caps or not caps.can_edit_own_content():
        return HttpResponseForbidden("You cannot edit this meal")

    edit_mf_id = request.GET.get("edit_food")

    mealfood = None
    if edit_mf_id:
        mealfood = get_object_or_404(
            MealFood,
            pk=edit_mf_id,
            meal=meal,
        )

    if request.method == "POST" and "save_food" in request.POST:
        mf_id = request.POST.get("mealfood_id")

        if mf_id:
            mf = get_object_or_404(MealFood, pk=mf_id, meal=meal)
            mf.quantity = request.POST.get("quantity")
            mf.save()
        else:
            MealFood.objects.create(
                meal=meal,
                food_id=request.POST.get("food_id"),
                quantity=request.POST.get("quantity"),
            )
    
    # ====== DPM FOOD PICKER ===========
    
    foods_payload = build_food_picker_foods_payload(Food.objects.all())

    meal_kpis = build_nutrition_kpis_from_meal(meal, user)
    
    dailyplan_kpis = build_nutrition_kpis_from_dailyplan(dailyplan, user)
    
    dpm_food_picker_ctx = build_dpm_food_picker_context_payload(
        meal=meal,
        meal_kpis=meal_kpis,
        dailyplan=dailyplan,
        dailyplan_kpis=dailyplan_kpis,
        mealfood=mealfood,
    )

    # ----- VIEW MODEL  ----

    vm = build_dpm_detail_vm(
        dailyplan,
        dpm,
        request.user,
        DAILYPLAN_MEAL_VIEWMODE_DEEP_EDIT,
    )

    context = vm.as_context()
    context["foods_json"] = json.dumps(foods_payload.as_list(), cls=DjangoJSONEncoder)
    context["food_picker_json"] = json.dumps(dpm_food_picker_ctx, cls=DjangoJSONEncoder)

    return render(
        request,
        "notas/dailyplan_meals/deep_edit.html",
        context,
    )



#************ AUXILIARES *********************

#Helper navegación
def _redirect_after_dpm_update(dailyplan):
    """
    Redirección consistente según estado del DailyPlan
    """
    if dailyplan.is_draft:
        return redirect("dailyplan_builder", dailyplan.pk)
    return redirect("dailyplan_edit", dailyplan.pk)


# ========== ACTIONS ====================

#ADD MEAL IN PICKER DAILYPLAN
@require_POST
@login_required
def dailyplan_add_meal(request, pk=None):
    dailyplan_id = request.POST.get("dailyplan_id") or pk

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=dailyplan_id,
        created_by=request.user,
    )

    meal_id = request.POST.get("meal_id")
    if not meal_id:
        messages.error(request, "Debes seleccionar una meal.")

        if dailyplan.is_draft:
            return redirect("dailyplan_builder", dailyplan.pk)
        return redirect("dailyplan_edit", dailyplan.pk)

    meal = get_object_or_404(Meal, pk=meal_id)

    hour = request.POST.get("hour") or None
    note = (request.POST.get("note") or "").strip() or None

    DailyPlanMeal.objects.create(
        dailyplan=dailyplan,
        meal=meal,
        hour=hour,
        note=note,
    )

    messages.success(request, "Meal added to daily plan")

    return _redirect_after_dpm_update(dailyplan)


@login_required
@require_POST
def dailyplanmeal_remove(request, dailyplan_id, dailyplanmeal_id):

    dpm = get_object_or_404(
        DailyPlanMeal.objects.select_related("dailyplan"),
        pk=dailyplanmeal_id,
        dailyplan__created_by=request.user,
    )

    dailyplan_id=dailyplan_id

    dailyplan = dpm.dailyplan
    dpm.delete()

    messages.success(request, "Meal eliminada del daily plan")

    return _redirect_after_dpm_update(dailyplan)


@login_required
@require_POST
def dailyplanmeal_update(request, dailyplan_id, dailyplanmeal_id):

    dailyplan = get_object_or_404(
        DailyPlan,
        id=dailyplan_id,
        created_by=request.user,
    )

    dpm = get_object_or_404(
        DailyPlanMeal.objects.select_related("dailyplan"),
        id=dailyplanmeal_id,
        dailyplan=dailyplan,
    )

    # ---------------------------
    # Meal (obligatoria)
    # ---------------------------
    meal_id = request.POST.get("meal_id")
    if not meal_id:
        messages.error(request, "Debes seleccionar una meal.")
        return _redirect_after_dpm_update(dailyplan)

    new_meal = get_object_or_404(Meal, id=meal_id)
    dpm.meal = new_meal

    # ---------------------------
    # Campos propios de DailyPlanMeal
    # ---------------------------
    dpm.hour = request.POST.get("hour") or None
    dpm.note = (request.POST.get("note") or "").strip() or None

    # ---------------------------
    # Persistencia
    # ---------------------------
    dpm.save()

    messages.success(request, "Meal actualizada correctamente.")

    return _redirect_after_dpm_update(dailyplan)


@login_required
def replace_meal(request, dailyplan_meal_id, new_meal_id):
    dailyplan_meal = get_object_or_404(DailyPlanMeal, id=dailyplan_meal_id)
    new_meal = get_object_or_404(Meal, id=new_meal_id)

    if dailyplan_meal.dailyplan.created_by != request.user:
        return redirect("dailyplan_detail", dailyplan_meal.dailyplan.id)

    dailyplan_meal.meal = new_meal
    dailyplan_meal.save()

    return redirect("dailyplan_detail", dailyplan_meal.dailyplan.id)


@login_required
@require_POST
def dailyplanmeal_create_meal(request, dailyplan_id, dailyplanmeal_id):

    dpm = get_object_or_404(
        DailyPlanMeal,
        pk=dailyplanmeal_id,
        dailyplan__id=dailyplan_id,
        dailyplan__created_by=request.user,
    )

    # Crear meal nueva vacía (contextual)
    new_meal = Meal.objects.create(
        name="New Meal",
        created_by=request.user,
        is_draft=True,
        is_public=False,
    )

    # Asignar al slot del DPM
    dpm.meal = new_meal
    dpm.save()

    messages.success(request, "Nueva meal creada en este slot")

    return redirect(
        "dailyplanmeal_deepedit",
        dailyplan_id=dailyplan_id,
        dailyplanmeal_id=dpm.id
    )









@login_required
def replace_dailyplan_meal(request, dailyplan_id, dailyplanmeal_id):
    
    dailyplan = get_object_or_404(
        DailyPlan,
        id=dailyplan_id,
        created_by=request.user,
    )

    dpm = get_object_or_404(
        DailyPlanMeal.objects.select_related("meal", "dailyplan"),
        id=dailyplanmeal_id,
        dailyplan=dailyplan,
    )

    original_meal = dpm.meal

    # Meal editable (draft nueva)
    replacement_meal = Meal.objects.create(
        name=f"{original_meal.name} (replacement)",
        created_by=request.user,
        is_draft=True,
        original_author=original_meal.created_by,
        forked_from=original_meal,
    )

    context = {
        "dailyplan_meal": dpm,
        "original_meal": original_meal,
        "replacement_meal": replacement_meal,
        "target_kpis": {
            "kcal": original_meal.total_kcal,
            "protein": original_meal.protein,
            "carbs": original_meal.carbs,
            "fat": original_meal.fat,
        },
    }

    return render(
        request,
        "notas/dailyplans/replace_meal.html",
        context,
    )


@require_POST
@login_required
def confirm_replace_meal(request, dpm_id, meal_id):
    dpm = get_object_or_404(
        DailyPlanMeal,
        pk=dpm_id,
        dailyplan__created_by=request.user,
    )

    new_meal = get_object_or_404(Meal, pk=meal_id)

    dpm.meal = new_meal
    dpm.save()

    messages.success(request, "Meal replaced successfully")

    return redirect("dailyplan_detail", pk=dpm.dailyplan.id)






@login_required
def attach_meal_to_existing_dpm(request, dpm_id, meal_id):

    dpm = get_object_or_404(
        DailyPlanMeal,
        pk=dpm_id,
        dailyplan__created_by=request.user
    )

    meal = get_object_or_404(Meal, pk=meal_id)

    # Copiar contexto del slot
    dpm.meal = meal
    dpm.save()

    # Saltar paso hora/note → ya existen
    return redirect("meal_configure", pk=meal.id)
