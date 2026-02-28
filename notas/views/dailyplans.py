from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notas.models import DailyPlan, DailyPlanMeal, Meal, DailyPlanShare
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from notas.actions.constants import (
    DAILYPLAN_VIEWMODE_LIST, 
    DAILYPLAN_VIEWMODE_DETAIL,
    DAILYPLAN_VIEWMODE_EDIT,
    DAILYPLAN_VIEWMODE_BUILD,
    DAILYPLAN_VIEWMODE_EXPLORE_LIST,
    DAILYPLAN_VIEWMODE_EXPLORE_DETAIL,
    DAILYPLAN_VIEWMODE_SHARED_LIST,
    DAILYPLAN_VIEWMODE_SHARED_DETAIL,
    DAILYPLAN_VIEWMODE_DRAFT_LIST,
)

from notas.services.capabilities import get_capabilities
from notas.services.kpis import build_nutrition_kpis_from_dailyplan

import json
from django.core.serializers.json import DjangoJSONEncoder
from notas.viewmodels.builder.dailyplan_detail_builder import build_dailyplan_detail_vm
from notas.viewmodels.builder.dailyplan_list_builder import build_dailyplan_list_vm
from notas.jscontext.builder.meal_picker_builder import build_meal_picker_meals_payload ,build_meal_picker_context_payload
from notas.services.dailyplan_queries import dailyplans_with_kcal, get_dailyplan_for_edit
from notas.services.access import get_dailyplan_for_user

from notas.forms import DailyPlanShareForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

import time




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
    dailyplans = (
        dailyplans_with_kcal()
        .filter(created_by=request.user, is_draft=False)
        .order_by("-created_at")
    )

    vm = build_dailyplan_list_vm(
        dailyplans,
        request.user,
        DAILYPLAN_VIEWMODE_LIST,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        vm.as_context(),
    )


@login_required
def dailyplan_explore_list(request):
    dailyplans = (
        dailyplans_with_kcal()
        .filter(is_public=True, is_draft=False)
        .order_by("-created_at")
    )

    vm = build_dailyplan_list_vm(
        dailyplans,
        request.user,
        DAILYPLAN_VIEWMODE_EXPLORE_LIST,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        vm.as_context(),
    )


@login_required
def dailyplan_shared_list(request):
    dailyplans = (
        dailyplans_with_kcal()
        .filter(
            shares__accepted_by=request.user,
            shares__removed=False,
            is_draft=False,
        )
        .prefetch_related("shares")
        .distinct()
    )


    vm = build_dailyplan_list_vm(
        dailyplans,
        request.user,
        DAILYPLAN_VIEWMODE_SHARED_LIST,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        vm.as_context(),
    )


@login_required
def dailyplan_draft_list(request):
    dailyplans = (
        dailyplans_with_kcal()
        .filter(
            created_by=request.user,
            is_draft=True
        )
        .order_by("-created_at")
    )

    vm = build_dailyplan_list_vm(
        dailyplans,
        request.user,
        DAILYPLAN_VIEWMODE_DRAFT_LIST,
    )

    return render(
        request,
        "notas/dailyplans/list.html",
        vm.as_context(),
    )




# DETAIL VIEWS ···················

@login_required
def dailyplan_detail(request, pk):

    dailyplan = get_dailyplan_for_user(request.user, pk)

    dailyplan_meals = dailyplan.meals_with_foods()

    vm = build_dailyplan_detail_vm(
        dailyplan,
        dailyplan_meals,
        request.user,
        DAILYPLAN_VIEWMODE_DETAIL,
    )

    return render(
        request,
        "notas/dailyplans/detail.html",
        vm.as_context(),
    )


@login_required
def dailyplan_explore_detail(request, pk):

    dailyplan = get_dailyplan_for_user(request.user, pk)

    dailyplan_meals = dailyplan.meals_with_foods()

    vm = build_dailyplan_detail_vm(
        dailyplan,
        dailyplan_meals,
        request.user,
        DAILYPLAN_VIEWMODE_EXPLORE_DETAIL,
    )

    return render(
        request,
        "notas/dailyplans/detail.html",
        vm.as_context(),
    )


@login_required
def dailyplan_share_detail(request, pk):

    dailyplan = get_dailyplan_for_user(request.user, pk)

    dailyplan_meals = dailyplan.meals_with_foods()

    vm = build_dailyplan_detail_vm(
        dailyplan,
        dailyplan_meals,
        request.user,
        DAILYPLAN_VIEWMODE_SHARED_DETAIL,
    )

    return render(
        request,
        "notas/dailyplans/detail.html",
        vm.as_context(),
    )


#************ RENDER DE EDICION *********************

# ---------- EDIT - BUILDER ----------

@login_required
def dailyplan_edit(request, pk):
    timings = {}
    t0 = time.perf_counter()

    # ==================================================
    # Aggregate load
    # ==================================================
    dailyplan = get_dailyplan_for_edit(request.user, pk)
    timings["dailyplan_fetch"] = time.perf_counter() - t0

    t1 = time.perf_counter()
    dailyplan_meals = dailyplan.meals_with_foods()
    timings["meals_with_foods"] = time.perf_counter() - t1

    user = request.user

    # ==================================================
    # Edit state
    # ==================================================
    t2 = time.perf_counter()
    edit_dpm_id = request.GET.get("edit_meal")
    dpm = None

    if edit_dpm_id:
        dpm = get_object_or_404(
            DailyPlanMeal.objects.select_related("meal"),
            pk=edit_dpm_id,
            dailyplan=dailyplan,
        )
    timings["edit_dpm_load"] = time.perf_counter() - t2

    # ==================================================
    # Meal picker payload
    # ==================================================
    t3 = time.perf_counter()
    meals = (
        Meal.objects
        .filter(is_draft=False)
        .order_by("name")
    )
    timings["meals_query"] = time.perf_counter() - t3

    t4 = time.perf_counter()
    meals_payload = build_meal_picker_meals_payload(meals)
    timings["meals_payload_build"] = time.perf_counter() - t4

    # ==================================================
    # Picker context
    # ==================================================
    t5 = time.perf_counter()
    dailyplan_kpis = build_nutrition_kpis_from_dailyplan(dailyplan, user)
    timings["dailyplan_kpis"] = time.perf_counter() - t5

    t6 = time.perf_counter()
    meal_picker_ctx = build_meal_picker_context_payload(
        dailyplan=dailyplan,
        dailyplan_kpis=dailyplan_kpis,
        dpm=dpm,
    )
    timings["picker_context"] = time.perf_counter() - t6

    # ==================================================
    # ViewModel
    # ==================================================
    t7 = time.perf_counter()
    vm = build_dailyplan_detail_vm(
        dailyplan,
        dailyplan_meals,
        user,
        DAILYPLAN_VIEWMODE_EDIT,
    )
    timings["vm_build"] = time.perf_counter() - t7

    # ==================================================
    # Serialization
    # ==================================================
    t8 = time.perf_counter()
    context = vm.as_context()
    context["meals_json"] = json.dumps(
        meals_payload.as_list(),
        cls=DjangoJSONEncoder,
    )
    timings["meals_json_dump"] = time.perf_counter() - t8

    t9 = time.perf_counter()
    context["meal_picker_context"] = json.dumps(
        meal_picker_ctx.as_dict(),
        cls=DjangoJSONEncoder,
    )
    timings["picker_context_dump"] = time.perf_counter() - t9

    timings["TOTAL"] = time.perf_counter() - t0

    # ==================================================
    # DEBUG OUTPUT (temporal)
    # ==================================================
    print("⏱ dailyplan_edit timings")
    for k, v in timings.items():
        print(f"  {k:<24}: {v:.4f}s")

    return render(
        request,
        "notas/dailyplans/edit.html",
        context,
    )


@login_required
def dailyplan_builder(request, pk):

    dailyplan = get_object_or_404(
        DailyPlan,
        pk=pk,
        created_by=request.user,
    )
    user = request.user 

    if not dailyplan.is_draft:
        return redirect("dailyplan_detail", pk=pk)

    #===== MODIFICICACION DATA ====================================================

    edit_dpm_id = request.GET.get("edit_meal")

    dpm = None

    if edit_dpm_id:
        dpm = get_object_or_404(
            DailyPlanMeal.objects.select_related("meal"),
            pk=edit_dpm_id,
            dailyplan=dailyplan,
        )

    dailyplan_meals = dailyplan.meals_with_foods()


    #===== PICKER LIST ====================================================

    meals = Meal.objects.filter(is_draft=False).order_by("name")
    meals_payload = build_meal_picker_meals_payload(meals)

    dailyplan_kpis = build_nutrition_kpis_from_dailyplan(dailyplan, user)
    meal_picker_ctx = build_meal_picker_context_payload(
        dailyplan=dailyplan,
        dailyplan_kpis=dailyplan_kpis,
        dpm=dpm,
    )
    
    # ======= VIEW MODEL ======================================

    vm = build_dailyplan_detail_vm(
        dailyplan,
        dailyplan_meals,
        user,
        DAILYPLAN_VIEWMODE_BUILD,
    )

    context = vm.as_context()
    context["meals_json"] = json.dumps(meals_payload.as_list(), cls=DjangoJSONEncoder)
    context["meal_picker_context"] = json.dumps(meal_picker_ctx.as_dict(), cls=DjangoJSONEncoder)


    return render(
        request,
        "notas/dailyplans/builder.html",
        context,
    )



#************ RENDER BÁSICOS *********************
# ---------- CREATE - RENAME - CONFIGURE ----------

@login_required
def dailyplan_create(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "El nombre es obligatorio")
            return redirect("dailyplan_create")

        dailyplan = DailyPlan.objects.create(
            name=name,
            created_by=request.user
        )
        return redirect("dailyplan_builder", pk=dailyplan.pk)

    return render(request, "notas/dailyplans/create.html")


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
        return redirect("dailyplan_builder", pk=pk)

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

    caps = get_capabilities(request.user)

    if request.method == "POST":
        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        # ---- reglas de negocio ----
        if is_public and not caps.can_publish():
            messages.error(request, "You cannot publish this daily plan.")
            return redirect("dailyplan_configure", pk=pk)

        if is_copiable and not caps.can_copy():
            messages.error(request, "Your plan does not allow copies.")
            return redirect("dailyplan_configure", pk=pk)

        dailyplan.is_public = is_public
        dailyplan.is_forkable = is_forkable
        dailyplan.is_copiable = is_copiable

        if dailyplan.is_draft:
            if not dailyplan.dailyplan_meals.exists():
                messages.error(
                    request,
                    "Add at least one meal before finalizing."
                )
                return redirect("dailyplan_detail", pk=pk)

            dailyplan.is_draft = False

        dailyplan.save()
        messages.success(request, "Daily plan saved.")
        return redirect("dailyplan_detail", pk=pk)

    return render(
        request,
        "notas/dailyplans/configure.html",
        {
            "dailyplan": dailyplan,
            "caps": caps,
        }
    )


#************ ACCIONES (NO RENDERIZAN) **************
# ---------- FORK - COPY ----------

@login_required
@require_POST
def dailyplan_fork(request, dailyplan_id):

    original = get_dailyplan_for_user(request.user, dailyplan_id)

    if not original.is_forkable:
        return HttpResponseForbidden("No puedes forkear este daily plan")

    forked = original.fork_for_user(request.user)

    messages.success(request, "Daily plan guardado en tu biblioteca")
    return redirect("dailyplan_detail", pk=forked.pk)


@login_required
@require_POST
def dailyplan_save(request, dailyplan_id):

    original = get_dailyplan_for_user(request.user, dailyplan_id)

    if not original.is_forkable:
        return HttpResponseForbidden("No puedes forkear este daily plan")

    forked = original.fork_for_user(request.user)

    messages.success(request, "Daily plan guardado en tu biblioteca")
    return redirect("dailyplan_list")


@login_required
@require_POST
def dailyplan_copy(request, pk):

    dailyplan = get_dailyplan_for_user(request.user, pk)

    if not dailyplan.is_copiable:
        return HttpResponseForbidden()

    copy = dailyplan.copy_for_user(request.user)

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
            return redirect("dailyplan_meal_create", dailyplan_id=dailyplan.id)

        meal = Meal.objects.create(
            name=name,
            created_by=request.user,
            is_draft=True,
            pending_dailyplan=dailyplan,
        )

        return redirect("meal_builder", pk=meal.id)

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
            "No puedes eliminar un dailyplan público."
        )

    dailyplan.delete()
    messages.success(request, "Daily plan eliminado definitivamente.")

    return redirect("dailyplan_list")




