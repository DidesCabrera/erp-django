from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from notas.application.services.access.capabilities import get_capabilities
from notas.domain.models import Meal, MealFood, DailyPlan, DailyPlanMeal, Food
from notas.presentation.config.viewmodel_config import (
    DAILYPLAN_MEAL_VIEWMODE_PERSONAL_DEEP_EDIT,
    DAILYPLAN_MEAL_VIEWMODE_DRAFT_DEEP_EDIT,
    DAILYPLAN_MEAL_VIEWMODE_DETAIL,
)
from notas.presentation.composition.viewmodel.dpm.detail_dpm_builder import build_dpm_detail_vm
from notas.presentation.composition.js.dpm_food_picker_builder import build_dpm_food_picker_context_payload
from notas.presentation.composition.js.food_picker_builder import build_food_picker_foods_payload
from notas.application.services.nutrition.nutrition_kpis import build_nutrition_kpis_from_meal, build_nutrition_kpis_from_dailyplan
import json
from django.core.serializers.json import DjangoJSONEncoder

from notas.presentation.viewmodels.base_vm import BaseVM
from notas.presentation.composition.viewmodel.ui_builder import build_ui_vm
from notas.application.services.commands.meal_commands import fork_meal_for_dailyplan

from django.urls import reverse

from notas.application.use_cases.dpm_pages import (
    get_dpm_detail_page_data,
    get_dpm_edit_page_data,
    get_dpm_deep_edit_page_data,
)


#************ RENDER COMPLEJOS *********************
# ---------- DETAIL (NO HAY LIST)  ----------

@login_required
def dailyplan_meal_detail(request, dailyplan_id, pk):

    page = get_dpm_detail_page_data(
        user=request.user,
        dailyplan_id=dailyplan_id,
        dpm_id=pk,
        viewmode=DAILYPLAN_MEAL_VIEWMODE_DETAIL,
    )

    content_vm = build_dpm_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        parents=[page.dailyplan],
        instance=page.meal,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplan_meals/detail.html",
        base_vm.as_context(),
    )


# ---------- EDIT - DEEP EDIT ----------

@login_required
def dailyplan_meal_edit(request, dailyplan_id, dailyplanmeal_id):

    page = get_dpm_edit_page_data(
        user=request.user,
        dailyplan_id=dailyplan_id,
        dpm_id=dailyplanmeal_id,
        viewmode=DAILYPLAN_MEAL_VIEWMODE_PERSONAL_DEEP_EDIT,
    )

    if request.method == "POST":
        page.dpm.hour = request.POST.get("hour") or None
        page.dpm.note = request.POST.get("note") or None
        page.dpm.save()
        return redirect("dailyplan_edit", pk=page.dailyplan.id)

    content_vm = build_dpm_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.dpm,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplan_meals/edit.html",
        base_vm.as_context(),
    )


@login_required
def dailyplanmeal_deepedit(request, dailyplan_id, dailyplanmeal_id):

    page = get_dpm_deep_edit_page_data(
        user=request.user,
        dailyplan_id=dailyplan_id,
        dpm_id=dailyplanmeal_id,
        request_get=request.GET,
        viewmode=DAILYPLAN_MEAL_VIEWMODE_PERSONAL_DEEP_EDIT,
    )

    caps = get_capabilities(request.user)
    if not caps or not caps.can_edit_own_content():
        return HttpResponseForbidden("You cannot edit this meal")

    if request.method == "POST" and "save_food" in request.POST:
        mf_id = request.POST.get("mealfood_id")

        if mf_id:
            mf = get_object_or_404(
                MealFood,
                pk=mf_id,
                meal=page.meal,
            )
            mf.quantity = request.POST.get("quantity")
            mf.save()
        else:
            MealFood.objects.create(
                meal=page.meal,
                food_id=request.POST.get("food_id"),
                quantity=request.POST.get("quantity"),
            )

        page = get_dpm_deep_edit_page_data(
            user=request.user,
            dailyplan_id=dailyplan_id,
            dpm_id=dailyplanmeal_id,
            request_get=request.GET,
            viewmode=DAILYPLAN_MEAL_VIEWMODE_PERSONAL_DEEP_EDIT,
        )

    content_vm = build_dpm_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        parents=[page.dailyplan],
        instance=page.meal,
        back_config={
            "type": "url",
            "value": reverse(
                "dailyplan_meal_detail",
                args=[page.dailyplan.id, page.dpm.id],
            ),
        },
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    context = base_vm.as_context()
    context["foods_json"] = page.foods_json
    context["food_picker_json"] = page.food_picker_context_json

    return render(
        request,
        "notas/dailyplan_meals/deep_edit.html",
        context,
    )


@login_required
def dailyplanmeal_draft_deepedit(request, dailyplan_id, dailyplanmeal_id):

    page = get_dpm_deep_edit_page_data(
        user=request.user,
        dailyplan_id=dailyplan_id,
        dpm_id=dailyplanmeal_id,
        request_get=request.GET,
        viewmode=DAILYPLAN_MEAL_VIEWMODE_DRAFT_DEEP_EDIT,
    )

    caps = get_capabilities(request.user)
    if not caps or not caps.can_edit_own_content():
        return HttpResponseForbidden("You cannot edit this meal")

    if request.method == "POST" and "save_food" in request.POST:
        mf_id = request.POST.get("mealfood_id")

        if mf_id:
            mf = get_object_or_404(
                MealFood,
                pk=mf_id,
                meal=page.meal,
            )
            mf.quantity = request.POST.get("quantity")
            mf.save()
        else:
            MealFood.objects.create(
                meal=page.meal,
                food_id=request.POST.get("food_id"),
                quantity=request.POST.get("quantity"),
            )

        page = get_dpm_deep_edit_page_data(
            user=request.user,
            dailyplan_id=dailyplan_id,
            dpm_id=dailyplanmeal_id,
            request_get=request.GET,
            viewmode=DAILYPLAN_MEAL_VIEWMODE_DRAFT_DEEP_EDIT,
        )

    content_vm = build_dpm_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        parents=[page.dailyplan],
        instance=page.meal,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    context = base_vm.as_context()
    context["foods_json"] = page.foods_json
    context["food_picker_json"] = page.food_picker_context_json

    return render(
        request,
        "notas/dailyplan_meals/deep_edit.html",
        context,
    )
#************ AUXILIARES *********************

# ========== ACTIONS ====================

# ADD MEAL IN PICKER DAILYPLAN
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
        return redirect("dailyplan_edit", dailyplan.pk)

    meal_original = get_object_or_404(
        Meal,
        pk=meal_id,
        created_by=request.user
    )

    meal = fork_meal_for_dailyplan(meal_original, request.user)

    hour = request.POST.get("hour") or None
    note = (request.POST.get("note") or "").strip() or None

    DailyPlanMeal.objects.create(
        dailyplan=dailyplan,
        meal=meal,
        hour=hour,
        note=note,
    )

    dailyplan.update_draft_status()

    messages.success(request, "Meal added to daily plan")

    return redirect("dailyplan_edit", dailyplan.pk)


@login_required
@require_POST
def dailyplanmeal_remove(request, dailyplan_id, dailyplanmeal_id):

    dpm = get_object_or_404(
        DailyPlanMeal.objects.select_related("dailyplan", "meal"),
        pk=dailyplanmeal_id,
        dailyplan__created_by=request.user,
    )

    dailyplan = dpm.dailyplan
    meal = dpm.meal   # 👈 guardar referencia

    # eliminar relación
    dpm.delete()

    # eliminar meal instance
    meal.delete()

    messages.success(request, "Meal eliminada del daily plan")

    return redirect("dailyplan_edit", dailyplan.pk)


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
        return redirect("dailyplan_edit", dailyplan.pk)

    selected_meal = get_object_or_404(
        Meal,
        id=meal_id,
        created_by=request.user,
    )

    if dpm.meal_id != selected_meal.id:
        replacement = fork_meal_for_dailyplan(selected_meal, request.user)
        old_meal = dpm.meal
        dpm.meal = replacement
        dpm.hour = request.POST.get("hour") or None
        dpm.note = (request.POST.get("note") or "").strip() or None
        dpm.save()

        if old_meal and old_meal.dailyplanmeal_set.count() == 0:
            old_meal.delete()
    else:
        dpm.hour = request.POST.get("hour") or None
        dpm.note = (request.POST.get("note") or "").strip() or None
        dpm.save()

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

    return redirect("dailyplan_edit", dailyplan.pk)

# LEGACY: this flow links meals directly and does not respect snapshot isolation.
# Keep temporarily until replacement flow is covered by tests and confirmed unused.
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





# LEGACY: this flow links meals directly and does not respect snapshot isolation.
# Keep temporarily until replacement flow is covered by tests and confirmed unused.
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
