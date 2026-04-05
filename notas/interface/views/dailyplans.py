from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notas.domain.models import DailyPlan, DailyPlanMeal, Meal, DailyPlanShare
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from notas.presentation.config.viewmodel_config import *

from notas.application.services.access.capabilities import get_capabilities
from notas.application.services.nutrition.nutrition_kpis import build_nutrition_kpis_from_dailyplan

import json
from django.core.serializers.json import DjangoJSONEncoder
from notas.presentation.composition.viewmodel.dailyplan.detail_dailyplan_builder import build_dailyplan_detail_vm
from notas.presentation.composition.viewmodel.dailyplan.list_dailyplan_builder import build_dailyplan_list_vm
from notas.presentation.composition.viewmodel.dailyplan.configure_dailyplan_builder import build_dailyplan_configure_vm
from notas.application.services.queries.dailyplan_queries import dailyplans_with_kcal, get_dailyplan_for_edit
from notas.application.services.queries.meal_queries import meals_with_kcal

from notas.application.services.access.access import get_dailyplan_for_user

from notas.interface.forms.forms import DailyPlanShareForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from notas.presentation.viewmodels.base_vm import BaseVM
from notas.presentation.composition.viewmodel.ui_builder import build_ui_vm

from notas.application.use_cases.dailyplan_pages import (
    get_dailyplan_edit_page_data,
    get_dailyplan_detail_page_data,
    get_dailyplan_list_page_data,
    get_dailyplan_explore_list_page_data,
    get_dailyplan_shared_list_page_data,
    get_dailyplan_draft_list_page_data,
)

from notas.application.services.commands.dailyplan_commands import (
    fork_dailyplan,
    copy_dailyplan,
    save_dailyplan,
)

#************ VIEW DE INBOX *********************

@login_required
def dailyplan_share(request, pk):

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=pk,
        created_by=request.user
    )

    # Solo el dueño puede compartir
    if dailyplan.created_by != request.user:
        return HttpResponseForbidden()

    form = DailyPlanShareForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["recipient_email"]

        share, created = DailyPlanShare.objects.get_or_create(
            sender=request.user,
            recipient_email=email,
            dailyplan=dailyplan,
        )

        link = request.build_absolute_uri(
            reverse("dailyplan_share_accept", args=[share.token])
        )

        send_mail(
            subject=f"{request.user.username} compartió un DailyPlan contigo",
            message=f"Te compartieron este plan:\n\n{link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return redirect("dailyplan_detail", pk=dailyplan.pk)

    return render(
        request,
        "notas/dailyplans/share.html",
        {"dailyplan": dailyplan, "form": form},
    )

@login_required
def dailyplan_share_accept(request, token):
    share = get_object_or_404(DailyPlanShare, token=token)

    # Marcar como aceptado
    share.accepted_by = request.user
    share.save()

    return redirect("inbox")

@login_required
def dailyplan_share_dismiss(request, share_id):
    share = get_object_or_404(
        DailyPlanShare,
        id=share_id,
        accepted_by=request.user
    )

    if request.method == "POST":
        share.dismissed = True
        share.save()

    return redirect("dailyplans_shared_with_me")

@login_required
@require_POST
def dailyplan_unshare(request, share_id):
    share = get_object_or_404(
        DailyPlanShare,
        id=share_id,
        accepted_by=request.user
    )

    share.removed = True
    share.save()

    return redirect("dailyplan_shared_list")


#************ RENDER COMPLEJOS *********************

# LIST VIEWS ···················
@login_required
def dailyplan_list(request):

    page = get_dailyplan_list_page_data(
        user=request.user,
    )

    content_vm = build_dailyplan_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        base_vm.as_context(),
    )

@login_required
def dailyplan_explore_list(request):

    page = get_dailyplan_explore_list_page_data(
        user=request.user,
    )

    content_vm = build_dailyplan_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        base_vm.as_context(),
    )

@login_required
def dailyplan_shared_list(request):

    page = get_dailyplan_shared_list_page_data(
        user=request.user,
    )

    content_vm = build_dailyplan_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        base_vm.as_context(),
    )

@login_required
def dailyplan_draft_list(request):

    page = get_dailyplan_draft_list_page_data(
        user=request.user,
    )

    content_vm = build_dailyplan_list_vm(
        page.list_content_data,
    )

    ui_vm = build_ui_vm(page.viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        base_vm.as_context(),
    )


# DETAIL VIEWS ···················

@login_required
def dailyplan_detail(request, pk):

    page = get_dailyplan_detail_page_data(
        user=request.user,
        dailyplan_id=pk,
        viewmode=DAILYPLAN_VIEWMODE_PERSONAL_DETAIL,
    )

    content_vm = build_dailyplan_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.dailyplan,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/detail.html",
        base_vm.as_context(),
    )

@login_required
def dailyplan_explore_detail(request, pk):

    page = get_dailyplan_detail_page_data(
        user=request.user,
        dailyplan_id=pk,
        viewmode=DAILYPLAN_VIEWMODE_EXPLORE_DETAIL,
    )

    content_vm = build_dailyplan_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.dailyplan,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/detail.html",
        base_vm.as_context(),
    )

@login_required
def dailyplan_shared_detail(request, pk):

    page = get_dailyplan_detail_page_data(
        user=request.user,
        dailyplan_id=pk,
        viewmode=DAILYPLAN_VIEWMODE_SHARED_DETAIL,
    )

    content_vm = build_dailyplan_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.dailyplan,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/detail.html",
        base_vm.as_context(),
    )

@login_required
def dailyplan_draft_detail(request, pk):

    page = get_dailyplan_detail_page_data(
        user=request.user,
        dailyplan_id=pk,
        viewmode=DAILYPLAN_VIEWMODE_DRAFT_DETAIL,
    )

    content_vm = build_dailyplan_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.dailyplan,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/detail.html",
        base_vm.as_context(),
    )


#************ RENDER DE EDICION *********************
# ---------- EDIT - BUILDER ----------


@login_required
def dailyplan_edit(request, pk):

    page = get_dailyplan_edit_page_data(
        user=request.user,
        dailyplan_id=pk,
        request_get=request.GET,
        is_draft=False,
    )

    content_vm = build_dailyplan_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.dailyplan,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    context = base_vm.as_context()
    context["meal_picker_data_json"] = page.meal_picker_data_json
    context["meal_picker_context"] = page.meal_picker_context_json
    context["selected_meal_id"] = page.selected_meal_id
    context["editing_dailyplanmeal_id"] = page.editing_dailyplanmeal_id

    return render(
        request,
        "notas/dailyplans/edit.html",
        context,
    )


@login_required
def dailyplan_draft_edit(request, pk):

    page = get_dailyplan_edit_page_data(
        user=request.user,
        dailyplan_id=pk,
        request_get=request.GET,
        is_draft=True,
    )

    content_vm = build_dailyplan_detail_vm(
        page.detail_content_data,
    )

    ui_vm = build_ui_vm(
        page.viewmode,
        instance=page.dailyplan,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    context = base_vm.as_context()
    context["meal_picker_data_json"] = page.meal_picker_data_json
    context["meal_picker_context"] = page.meal_picker_context_json
    context["selected_meal_id"] = page.selected_meal_id
    context["editing_dailyplanmeal_id"] = page.editing_dailyplanmeal_id

    return render(
        request,
        "notas/dailyplans/edit.html",
        context,
    )



#************ RENDER BÁSICOS *********************
# ---------- CREATE - RENAME - CONFIGURE ----------

@login_required
def dailyplan_create(request):

    viewmode = DAILYPLAN_VIEWMODE_CREATE

    ui_vm = build_ui_vm(viewmode)

    base_vm = BaseVM(
        ui=ui_vm,
        content=None,
    )

    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "El nombre es obligatorio")
            return redirect("dailyplan_create")

        dailyplan = DailyPlan.objects.create(
            name=name,
            created_by=request.user
        )
        return redirect("dailyplan_edit", pk=dailyplan.pk)

    return render(
        request,
         "notas/dailyplans/create.html",
         base_vm.as_context(),

    )

@login_required
def dailyplan_rename(request, pk):
    dailyplan = get_object_or_404(
        DailyPlan,
        pk=pk,
        created_by=request.user,
    )

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "El nombre no puede estar vacío.")
            return redirect("dailyplan_rename", pk=pk)

        dailyplan.name = name
        dailyplan.save()

        messages.success(request, "Nombre actualizado.")
        return redirect("dailyplan_edit", pk=pk)

    return render(
        request,
        "notas/dailyplans/rename.html",
        {"dailyplan": dailyplan}
    )


@login_required
def dailyplan_configure(request, pk):

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=pk,
        created_by=request.user,
    )

    user = request.user
    caps = get_capabilities(user)

    if not caps or not caps.can_access_distribution_settings():
        messages.error(request, "Your plan cannot configure daily plan distribution.")
        return redirect("dailyplan_edit", pk=pk)

    # =====================
    # POST
    # =====================

    if request.method == "POST":

        is_public   = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        if is_public and not caps.can_publish():
            messages.error(request, "You cannot publish this daily plan.")
            return redirect("dailyplan_configure", pk=pk)

        if is_copiable and not caps.can_copy():
            messages.error(request, "Your plan does not allow copies.")
            return redirect("dailyplan_configure", pk=pk)

        dailyplan.is_public = is_public
        dailyplan.is_forkable = is_forkable
        dailyplan.is_copiable = is_copiable

        dailyplan.save()

        messages.success(request, "Configuración guardada")

        return redirect("dailyplan_edit", pk=pk)

    # =====================
    # VIEWMODEL
    # =====================

    viewmode = DAILYPLAN_VIEWMODE_CONFIGURE

    content_vm = build_dailyplan_configure_vm(
        dailyplan,
        user,
        viewmode,
    )

    ui_vm = build_ui_vm(
        viewmode,
        instance=dailyplan,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/dailyplans/configure.html",
        base_vm.as_context(),
    )


#************ ACCIONES (NO RENDERIZAN) **************
# ---------- FORK - COPY ----------

@login_required
@require_POST
def dailyplan_fork(request, dailyplan_id):

    original = get_dailyplan_for_user(request.user, dailyplan_id)

    if not original.is_forkable:
        return HttpResponseForbidden("No puedes forkear este daily plan")

    forked = fork_dailyplan(original, request.user)

    messages.success(request, "Daily plan guardado en tu biblioteca")
    return redirect("dailyplan_detail", pk=forked.pk)


@login_required
@require_POST
def dailyplan_save(request, dailyplan_id):

    original = get_dailyplan_for_user(request.user, dailyplan_id)

    if not original.is_forkable:
        return HttpResponseForbidden("No puedes forkear este daily plan")

    forked = fork_dailyplan(original, request.user)

    messages.success(request, "Daily plan guardado en tu biblioteca")
    return redirect("dailyplan_list")


@login_required
@require_POST
def dailyplan_copy(request, pk):

    dailyplan = get_dailyplan_for_user(request.user, pk)

    if not dailyplan.is_copiable:
        return HttpResponseForbidden()

    copy = copy_dailyplan(dailyplan, request.user)

    messages.success(request, "Daily plan copied successfully")
    return redirect("dailyplan_detail", pk=copy.pk)


#CREATE MEAL DESDE EDIT DAILYPLAN
@login_required
def create_meal_for_dailyplan(request, dailyplan_id):

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=dailyplan_id,
        created_by=request.user,
    )

    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Name is required")
            return redirect("create_meal_for_dailyplan", dailyplan_id=dailyplan.id)

        meal = Meal.objects.create(
            name=name,
            created_by=request.user,
            is_draft=True,
            pending_dailyplan=dailyplan,
        )

        return redirect("meal_edit", pk=meal.id)

    return render(
        request,
        "notas/meals/create.html",
        {"dailyplan": dailyplan},
    )


#CREATE DPM AFTER SET HOUE NOTE (STEP 3 FLOW)
@login_required
def attach_meal_to_dailyplan(request, dailyplan_id, meal_id):

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=dailyplan_id,
        created_by=request.user,
    )

    meal = get_object_or_404(Meal, pk=meal_id, created_by=request.user)

    if request.method == "POST":
        hour = request.POST.get("hour") or None
        note = request.POST.get("note") or None

        DailyPlanMeal.objects.create(
            dailyplan=dailyplan,
            meal=meal,
            hour=hour,
            note=note,
        )
        dailyplan.update_draft_status()

        return redirect("meal_configure", pk=meal.id)

    return render(
        request,
        "notas/dailyplans/attach_meal.html",
        {
            "dailyplan": dailyplan,
            "meal": meal,
        }
    )


#ADD MEAL FROM MEAL_LIST (SELECT DAILYPLAN AND SET HOUR-NOTA)
@login_required
def add_meal_from_list(request, meal_id):
    """
    Paso intermedio:
    - elegir dailyplan
    - definir hora
    - agregar nota
    """
    meal = get_object_or_404(Meal, pk=meal_id)

    # 🔹 solo MIS dailyplans (drafts por ahora)
    dailyplans = DailyPlan.objects.filter(
        created_by=request.user
    ).order_by("-created_at")

    return render(
        request,
        "notas/dailyplans/add_meal_from_list.html",
        {
            "meal": meal,
            "dailyplans": dailyplans,
        },
    )



#----

@login_required
@require_POST
def dailyplan_remove(request, pk):
    dailyplan = get_object_or_404(
        DailyPlan,
        pk=pk,
        created_by=request.user
    )

    # 🔒 reglas de seguridad
    if dailyplan.is_public:
        return HttpResponseForbidden(
            "No puedes eliminar un plan público."
        )

    dailyplan.delete()
    messages.success(request, "Plan eliminado definitivamente.")

    return redirect("dailyplan_list")




