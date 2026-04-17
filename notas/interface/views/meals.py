from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from notas.application.services.access.capabilities import get_capabilities
from notas.domain.models import Meal, MealFood, Food, MealShare
from notas.presentation.config.viewmodel_config import *

import json
from django.core.serializers.json import DjangoJSONEncoder
from notas.application.services.nutrition.nutrition_kpis import build_nutrition_kpis_from_meal
from notas.presentation.composition.viewmodel.meal.detail_meal_builder import build_meal_detail_vm
from notas.presentation.composition.viewmodel.meal.list_meal_builder import build_meal_list_vm
from notas.presentation.composition.viewmodel.meal.configure_meal_builder import build_meal_configure_vm
from notas.presentation.composition.js.food_picker_builder import build_food_picker_foods_payload, build_food_picker_context_payload
from notas.application.services.queries.meal_queries import meals_with_kcal

from notas.interface.forms.forms import MealShareForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from notas.presentation.viewmodels.base_vm import BaseVM
from notas.presentation.composition.viewmodel.ui_builder import build_ui_vm
from notas.application.use_cases.meal_pages import get_meal_detail_page_data

from notas.application.use_cases.meal_pages import (
    get_meal_detail_page_data,
    get_meal_list_page_data,
    get_meal_explore_list_page_data,
    get_meal_shared_list_page_data,
    get_meal_draft_list_page_data,
)

from notas.application.services.commands.meal_commands import (
    fork_meal_for_library,
    copy_meal,
    save_meal,
)



#************ VIEW DE INBOX *********************

@login_required
def meal_share(request, pk):

    meal = get_object_or_404(
        Meal,
        pk=pk,
        created_by=request.user
    )

    # Solo el dueño puede compartir
    if meal.created_by != request.user:
        return HttpResponseForbidden()

    form = MealShareForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["recipient_email"]

        share, created = MealShare.objects.get_or_create(
            sender=request.user,
            recipient_email=email,
            meal=meal,
        )

        link = request.build_absolute_uri(
            reverse("meal_share_accept", args=[share.token])
        )

        send_mail(
            subject=f"{request.user.username} compartió una Meal contigo",
            message=f"Te compartieron este plan:\n\n{link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return redirect("meal_detail", pk=meal.pk)

    return render(
        request,
        "notas/meals/share.html",
        {"meal": meal, "form": form},
    )


@login_required
def meal_share_accept(request, token):
    share = get_object_or_404(MealShare, token=token)

    # Marcar como aceptado
    share.accepted_by = request.user
    share.save()

    return redirect("meal_shared_list")


@login_required
def meal_share_dismiss(request, share_id):
    share = get_object_or_404(
        MealShare,
        id=share_id,
        accepted_by=request.user
    )

    if request.method == "POST":
        share.dismissed = True
        share.save()

    return redirect("meal_shared_list")


@login_required
@require_POST
def meal_unshare(request, share_id):

    share = get_object_or_404(
        MealShare,
        id=share_id,
        accepted_by=request.user,
    )

    share.removed = True
    share.save()

    messages.success(request, "Meal removida de Shared with me.")
    return redirect("meal_shared_list")



#************ RENDER COMPLEJOS *********************

# LIST VIEWS ···················

@login_required
def meal_list(request):

    page = get_meal_list_page_data(
        user=request.user,
    )

    content_vm = build_meal_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/meals/list.html",
        base_vm.as_context(),
    )
    

@login_required
def meal_explore_list(request):

    page = get_meal_explore_list_page_data(
        user=request.user,
    )

    content_vm = build_meal_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/meals/list.html",
        base_vm.as_context(),
    )


@login_required
def meal_shared_list(request):

    page = get_meal_shared_list_page_data(
        user=request.user,
    )

    content_vm = build_meal_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/meals/list.html",
        base_vm.as_context(),
    )


@login_required
def meal_draft_list(request):

    page = get_meal_draft_list_page_data(
        user=request.user,
    )

    content_vm = build_meal_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/meals/list.html",
        base_vm.as_context(),
    )


# DETAIL VIEWS ···················

@login_required
def meal_detail(request, pk):

    page = get_meal_detail_page_data(
        user=request.user,
        meal_id=pk,
        viewmode=MEAL_VIEWMODE_PERSONAL_DETAIL,
        request_get=request.GET,
    )

    meal = page.meal

    if request.method == "POST":

        if "finish_for_dailyplan" in request.POST:
            if meal.pending_dailyplan:
                dailyplan_id = meal.pending_dailyplan.id

                meal.pending_dailyplan = None
                meal.save(update_fields=["pending_dailyplan"])

                return redirect(
                    reverse("dailyplan_detail", args=[dailyplan_id]) +
                    f"?select_meal={meal.id}"
                )

        elif "save_food" in request.POST:
            mf_id = request.POST.get("mealfood_id")
            quantity = request.POST.get("quantity")
            food_id = request.POST.get("food_id")

            if mf_id:
                mf = get_object_or_404(
                    MealFood,
                    pk=mf_id,
                    meal=meal,
                )
                mf.quantity = quantity
                mf.save()
            else:
                MealFood.objects.create(
                    meal=meal,
                    food_id=food_id,
                    quantity=quantity,
                )

            meal = Meal.objects.get(pk=meal.pk)
            meal.update_draft_status()

            return redirect("meal_detail", pk=meal.id)

    content_vm = build_meal_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.meal,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    context = base_vm.as_context()

    context["show_return_to_dailyplan"] = page.show_return_to_dailyplan
    context["foods_json"] = page.foods_json
    context["food_picker_context"] = page.food_picker_context_json
    context["editing_mealfood_id"] = page.editing_mealfood_id
    context["selected_food_id"] = page.selected_food_id

    return render(
        request,
        "notas/meals/detail.html",
        context,
    )



@login_required
def meal_explore_detail(request, pk, dailyplan_id=None):

    page = get_meal_detail_page_data(
        user=request.user,
        meal_id=pk,
        viewmode=MEAL_VIEWMODE_EXPLORE_DETAIL,
    )

    content_vm = build_meal_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.meal,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/meals/detail.html",
        base_vm.as_context(),
    )


@login_required
def meal_share_detail(request, pk, dailyplan_id=None):

    page = get_meal_detail_page_data(
        user=request.user,
        meal_id=pk,
        viewmode=MEAL_VIEWMODE_SHARED_DETAIL,
    )

    content_vm = build_meal_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.meal,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/meals/detail.html",
        base_vm.as_context(),
    )


#************ RENDER BÁSICOS *********************
# ---------- CREATE - RENAME - CONFIGURE ----------

@login_required
def meal_create(request):

    from_dailyplan = request.GET.get("from_dailyplan")

    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "El nombre es obligatorio")
            return redirect("meal_create")

        # 1. Crear meal draft
        meal = Meal.objects.create(
            name=name,
            created_by=request.user,
            is_draft=True
        )

        # 2. Guardar contexto en el modelo (solo si aplica)
        if from_dailyplan:
            meal.pending_dailyplan_id = from_dailyplan
            meal.save()

        # 3. Ir siempre al builder normal
        return redirect("meal_detail", pk=meal.id)

    viewmode = MEAL_VIEWMODE_CREATE

    ui_vm = build_ui_vm(viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=None,
    )

    return render(
        request,
         "notas/meals/create.html",
         base_vm.as_context(),

    )

@login_required
def meal_rename(request, pk):
    meal = get_object_or_404(Meal, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "El nombre no puede estar vacío.")
            return redirect("meal_rename", pk=meal.pk)

        meal.name = name
        meal.save()

        messages.success(request, "Nombre actualizado correctamente.")
        return redirect("meal_detail", pk=pk)

    header = {"title": "Edit meal name"}

    return render(request, "notas/meals/rename.html", {
        "meal": meal,
        "header": header,
    })


@login_required
def meal_configure(request, pk):

    meal = get_object_or_404(
        Meal,
        pk=pk,
        created_by=request.user,
    )

    user = request.user
    caps = get_capabilities(user)

    if not caps or not caps.can_access_distribution_settings():
        messages.error(request, "Your plan cannot configure meal distribution.")
        return redirect("meal_detail", pk=pk)

    # =====================
    # POST
    # =====================

    if request.method == "POST":

        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        if is_public and not caps.can_publish():
            messages.error(request, "You cannot publish this meal.")
            return redirect("meal_configure", pk=pk)

        if is_copiable and not caps.can_copy():
            messages.error(request, "Your plan does not allow copies.")
            return redirect("meal_configure", pk=pk)

        meal.is_public = is_public
        meal.is_forkable = is_forkable
        meal.is_copiable = is_copiable

        origin_dailyplan = meal.pending_dailyplan

        meal.save()

        if origin_dailyplan:

            meal.pending_dailyplan = None
            meal.save(update_fields=["pending_dailyplan"])

            messages.success(
                request,
                "Meal saved and added to your DailyPlan."
            )

            return redirect(
                "dailyplan_detail",
                pk=origin_dailyplan.id
            )

        messages.success(request, "Configuration saved")
        return redirect("meal_detail", pk=pk)

    # =====================
    # VIEWMODEL
    # =====================

    viewmode = MEAL_VIEWMODE_CONFIGURE

    content_vm = build_meal_configure_vm(
        meal,
        user,
        viewmode
    )

    ui_vm = build_ui_vm(
        viewmode,
        instance=meal
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm
    )

    context = base_vm.as_context()

    return render(
        request,
        "notas/meals/configure.html",
        context
    )

#************ ACCIONES (NO RENDERIZAN) **************
# ---------- FORK - COPY ----------


@login_required
@require_POST
def meal_fork(request, meal_id):

    original = get_object_or_404(Meal, id=meal_id)

    if not original.is_forkable:
        return HttpResponseForbidden("No puedes forkear esta meal")

    forked = fork_meal_for_library(original, request.user)

    messages.success(request, "Meal guardada en tu biblioteca")
    return redirect("meal_detail", pk=forked.pk)


@login_required
@require_POST
def meal_copy(request, pk):

    original = get_object_or_404(Meal, pk=pk)

    if not original.is_copiable:
        return HttpResponseForbidden("No tienes permiso para copiar esta meal")

    copy = copy_meal(original, request.user)

    messages.success(request, "Meal copiada correctamente")
    return redirect("meal_detail", pk=copy.pk)


@login_required
@require_POST
def meal_remove(request, pk):

    meal = get_object_or_404(
        Meal,
        pk=pk,
        created_by=request.user
    )

    meal.delete()

    messages.success(request, "Meal removida de tu lista.")
    return redirect("meal_list")


@login_required
@require_POST
def meal_draft_delete(request, pk):

    meal = get_object_or_404(
        Meal,
        pk=pk,
        created_by=request.user,
        is_draft=True
    )

    meal.delete()

    messages.success(request, "Draft eliminado definitivamente.")
    return redirect("meal_draft_list")


