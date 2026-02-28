from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from notas.services.capabilities import get_capabilities
from notas.models import Meal, MealFood, Food, MealShare
from notas.actions.constants import (
    MEAL_VIEWMODE_LIST, 
    MEAL_VIEWMODE_DETAIL,
    MEAL_VIEWMODE_EDIT,
    MEAL_VIEWMODE_EXPLORE_LIST,
    MEAL_VIEWMODE_EXPLORE_DETAIL,
    MEAL_VIEWMODE_DRAFT_LIST,
    MEAL_VIEWMODE_SHARED_LIST,
    MEAL_VIEWMODE_SHARED_DETAIL,
)

import json
from django.core.serializers.json import DjangoJSONEncoder
from notas.services.kpis import build_nutrition_kpis_from_meal
from notas.viewmodels.builder.meal_detail_builder import build_meal_detail_vm
from notas.viewmodels.builder.meal_list_builder import build_meal_list_vm
from notas.jscontext.builder.food_picker_builder import build_food_picker_foods_payload, build_food_picker_context_payload
from notas.services.meal_queries import meals_with_kcal

from notas.forms import MealShareForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


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

    return redirect("inbox")


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

    return redirect("meals_shared_with_me")


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

    meals = (
        meals_with_kcal()
        .filter(created_by=request.user, is_draft=False)
        .order_by("-created_at")
    )

    vm = build_meal_list_vm(
        meals,
        request.user,
        MEAL_VIEWMODE_LIST,
    )

    return render(
        request,
        "notas/meals/list.html",
        vm.as_context(),
    )


@login_required
def meal_explore_list(request):

    meals = (
        meals_with_kcal()
        .filter(is_public=True, is_draft=False)
        .order_by("-created_at")
    )

    vm = build_meal_list_vm(
        meals,
        request.user,
        MEAL_VIEWMODE_EXPLORE_LIST,
    )

    return render(
        request,
        "notas/meals/list.html",
        vm.as_context(),
    )


@login_required
def meal_shared_list(request):

    meals = (
        meals_with_kcal()
        .filter(
            shares__accepted_by=request.user,
            shares__removed=False,
            is_draft=False,
        )
        .prefetch_related("shares")
        .distinct()
    )

    vm = build_meal_list_vm(
        meals,
        request.user,
        MEAL_VIEWMODE_SHARED_LIST,
    )

    return render(
        request,
        "notas/meals/list.html",
        vm.as_context(),
    )


@login_required
def meal_draft_list(request):

    meals = (
        meals_with_kcal()
        .filter(
            created_by=request.user,
            is_draft=True
        )
        .order_by("-created_at")
    )

    vm = build_meal_list_vm(
        meals,
        request.user,
        MEAL_VIEWMODE_DRAFT_LIST,
    )

    return render(
        request,
        "notas/meals/list.html",
        vm.as_context(),
    )



# DETAIL VIEWS ···················

@login_required
def meal_detail(request, pk, dailyplan_id=None):

    meal = (
        Meal.objects
        .prefetch_related("meal_food_set", "meal_food_set__food")
        .get(pk=pk, created_by=request.user)
    )

    vm = build_meal_detail_vm(
        meal,
        request.user,
        MEAL_VIEWMODE_DETAIL,
    )

    return render(
        request,
        "notas/meals/detail.html",
        vm.as_context(),
    )


@login_required
def meal_explore_detail(request, pk, dailyplan_id=None):

    meal = (
        Meal.objects
        .prefetch_related("meal_food_set", "meal_food_set__food")
        .get(pk=pk, created_by=request.user)
    )

    vm = build_meal_detail_vm(
        meal,
        request.user,
        MEAL_VIEWMODE_EXPLORE_DETAIL,
    )

    return render(
        request,
        "notas/meals/detail.html",
        vm.as_context(),
    )


@login_required
def meal_share_detail(request, pk, dailyplan_id=None):

    meal = (
        Meal.objects
        .prefetch_related("meal_food_set", "meal_food_set__food")
        .get(pk=pk)
    )

    vm = build_meal_detail_vm(
        meal,
        request.user,
        MEAL_VIEWMODE_SHARED_DETAIL,
    )

    return render(
        request,
        "notas/meals/detail.html",
        vm.as_context(),
    )



#************ RENDER DE EDICION *********************

# ---------- EDIT - BUILDER ----------

@login_required
def meal_edit(request, pk):

    meal = (
        Meal.objects
        .prefetch_related("meal_food_set", "meal_food_set__food")
        .get(pk=pk)
    )

    user = request.user

    caps = get_capabilities(user)

    if not caps or not caps.can_edit_own_content():
        return HttpResponseForbidden("You cannot edit this meal")

    #===== MODIFICICACION DATA ====================================================

    edit_mf_id = request.GET.get("edit_food")
    mealfood = None

    if edit_mf_id:
        mealfood = get_object_or_404(
            MealFood, 
            pk=edit_mf_id, 
            meal=meal
        )

    if request.method == "POST":
        if "save_food" in request.POST:
            mf_id = request.POST.get("mealfood_id")

            if mf_id:
                mf = get_object_or_404(MealFood, pk=mf_id, meal=meal)
                mf.quantity = request.POST.get("quantity")
                mf.save()
            else:
                MealFood.objects.create(
                    meal=meal,
                    food_id=request.POST.get("food_id"),
                    quantity=request.POST.get("quantity")
                )

    # ===== FOOD PICKER ====================================================
   
    foods_payload = build_food_picker_foods_payload(Food.objects.all())
    
    nutrition_kpis = build_nutrition_kpis_from_meal(meal, user)
    food_picker_ctx = build_food_picker_context_payload(
        meal=meal,
        nutrition_kpis=nutrition_kpis,
        mealfood=mealfood,
    )

    # ======= VIEW MODEL ======================================

    vm = build_meal_detail_vm(
        meal,
        user,
        MEAL_VIEWMODE_EDIT,
    )

    context = vm.as_context()
    context["foods_json"] = json.dumps(foods_payload.as_list(), cls=DjangoJSONEncoder)
    context["food_picker_context"] = json.dumps(food_picker_ctx.as_dict(), cls=DjangoJSONEncoder)


    return render(
        request,
        "notas/meals/edit.html",
        context,
    )


@login_required
def meal_builder(request, pk):

    meal = (
        Meal.objects
        .prefetch_related("meal_food_set", "meal_food_set__food")
        .get(pk=pk, created_by=request.user)
    )

    user = request.user

    if not meal.is_draft:
        return redirect("meal_edit", pk=meal.pk)

    caps = get_capabilities(request.user)

    if not caps or not caps.can_edit_own_content():
        return HttpResponseForbidden("You cannot edit this meal")

    #===== MODIFICICACION DATA =================---------------------------

    edit_mf_id = request.GET.get("edit_food")
    mealfood = None

    if edit_mf_id:
        mealfood = get_object_or_404(
            MealFood,
            pk=edit_mf_id,
            meal=meal,
        )
    
    # ===== FOOD PICKER ====================================================
   
    foods_payload = build_food_picker_foods_payload(Food.objects.all())

    nutrition_kpis = build_nutrition_kpis_from_meal(meal, user)
    food_picker_ctx = build_food_picker_context_payload(
        meal=meal,
        nutrition_kpis=nutrition_kpis,
        mealfood=mealfood,
    )

    vm = build_meal_detail_vm(
        meal,
        user,
        MEAL_VIEWMODE_EDIT,
    )

    if meal.pending_dailyplan:
        continue_url = reverse(
            "dailyplan_attach_meal",
            args=[meal.pending_dailyplan.id, meal.id],
        )
    else:
        continue_url = reverse(
            "meal_configure",
            args=[meal.id],
        )


    context = vm.as_context()
    context["foods_json"] = json.dumps(foods_payload.as_list(), cls=DjangoJSONEncoder)
    context["food_picker_context"] = json.dumps(food_picker_ctx.as_dict(), cls=DjangoJSONEncoder)
    context["continue_url"] = continue_url

    return render(
        request,
        "notas/meals/builder.html",
        context
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
        return redirect("meal_builder", pk=meal.id)

    # GET → solo renderiza form
    return render(request, "notas/meals/create.html")


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
        return redirect("meal_builder", pk=pk)

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

    caps = get_capabilities(request.user)

    if request.method == "POST":
        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        # ---- reglas de negocio ----
        if is_public and not caps.can_publish():
            messages.error(request, "You cannot publish this meal.")
            return redirect("meal_configure", pk=pk)

        if is_copiable and not caps.can_copy():
            messages.error(request, "Your plan does not allow copies.")
            return redirect("meal_configure", pk=pk)

        # ---- aplicar flags ----
        meal.is_public = is_public
        meal.is_forkable = is_forkable
        meal.is_copiable = is_copiable

        # ---- finalizar draft ----
        if meal.is_draft:
            if not meal.meal_food_set.exists():
                messages.error(
                    request,
                    "Add at least one food before finalizing."
                )
                return redirect("meal_detail", pk=pk)

            meal.is_draft = False

        # ==========================================
        # ✅ CONTEXTO: volver al DailyPlan si existe
        # ==========================================

        origin_dailyplan = meal.pending_dailyplan

        # guardar meal primero
        meal.save()

        # si venía desde un dailyplan → cerrar flujo
        if origin_dailyplan:
            meal.pending_dailyplan = None
            meal.save()

            messages.success(
                request,
                "Meal saved and added to your DailyPlan."
            )
            return redirect(
                "dailyplan_edit",
                pk=origin_dailyplan.id
            )

        # ---- flujo normal ----
        messages.success(request, "Meal saved.")
        return redirect("meal_detail", pk=pk)

    return render(
        request,
        "notas/meals/configure.html",
        {
            "meal": meal,
            "caps": caps,
        }
    )


#************ ACCIONES (NO RENDERIZAN) **************
# ---------- FORK - COPY ----------


@login_required
@require_POST
def meal_fork(request, meal_id):

    original = get_object_or_404(Meal, id=meal_id)

    if not original.is_forkable:
        return HttpResponseForbidden("No puedes forkear esta meal")

    forked = original.fork_for_user(request.user)

    messages.success(request, "Meal guardada en tu biblioteca")
    return redirect("meal_detail", pk=forked.pk)


@login_required
@require_POST
def meal_copy(request, pk):

    original = get_object_or_404(Meal, pk=pk)

    if not original.is_copiable:
        return HttpResponseForbidden("No tienes permiso para copiar esta meal")

    copy = original.copy_for_user(request.user)

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

    # Solo permitir remove si fue guardado (fork)
    if meal.forked_from is None:
        return HttpResponseForbidden(
            "No puedes remover una meal original, solo una guardada."
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
