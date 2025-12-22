from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notas.models import DailyPlan, DailyPlanMeal, Meal
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from notas.services.permissions import can_copy, can_fork, can_publish
from django.contrib import messages
from notas.actions.resolvers import resolve_meal_actions
from notas.models import DailyPlan
from notas.actions.meal_resolvers import resolve_meal_actions
from notas.actions.dailyplan import resolve_dailyplan_actions
from notas.actions.dailyplan_meal import resolve_dailyplan_meal_actions
from django.urls import reverse
from notas.routing.meal import meal_url
from notas.actions.constants import MEAL_CONTEXT_DAILYPLAN



@login_required
@require_POST
def fork_dailyplan(request, dailyplan_id):

    original = get_object_or_404(DailyPlan, id=dailyplan_id)
    profile = request.user.profile

    if not can_fork(profile) or not original.is_forkable:
        return HttpResponseForbidden("No puedes forkear este daily plan")

    forked = DailyPlan.objects.create(
        name=f"{original.name} (fork)",
        created_by=request.user,
        original_author=(
            original.original_author
            if original.original_author
            else original.created_by
        ),
        forked_from=original,
        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    for dpm in original.daily_plan_meals.all():
        DailyPlanMeal.objects.create(
            daily_plan=forked,
            meal=dpm.meal,
            title=dpm.title,
            hour=dpm.hour,
            order=dpm.order
        )

    messages.success(request, "Daily plan forked successfully")
    return redirect("dailyplan_detail", pk=forked.pk)


@login_required
@require_POST
def copy_dailyplan(request, pk):

    dailyplan = get_object_or_404(DailyPlan, pk=pk)
    profile = request.user.profile

    if not can_copy(profile) or not dailyplan.is_copiable:
        return HttpResponseForbidden("No puedes copiar este daily plan")

    copy = DailyPlan.objects.create(
        name=f"{dailyplan.name} (copy)",
        created_by=request.user,
        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    for dpm in dailyplan.daily_plan_meals.all():
        DailyPlanMeal.objects.create(
            daily_plan=copy,
            meal=dpm.meal,
            title=dpm.title,
            hour=dpm.hour,
            order=dpm.order,
        )

    messages.success(request, "Daily plan copied successfully")
    return redirect("dailyplan_detail", pk=copy.pk)


@login_required
def dailyplan_list(request):
    dailyplans = DailyPlan.objects.filter(
        created_by=request.user
    ).order_by("-created_at")

    for dp in dailyplans:
        dp.actions = resolve_dailyplan_actions(dp, user=request.user)

    items = []

    for dp in dailyplans:
        items.append({
            "dailyplan": dp,
            "children": dp.daily_plan_meals.select_related("meal"),
            "actions": resolve_dailyplan_actions(dp, request.user),
        })

    return render(
        request,
        "notas/dailyplans/list.html",
        {
            "items": items,
        },
    )

@login_required
def dailyplan_detail(request, pk):
    dailyplan = get_object_or_404(
        DailyPlan,
        pk=pk,
        created_by=request.user,
    )

    # Meals disponibles para el formulario "Add meal"
    meals = Meal.objects.all().order_by("name")

    # ViewModel para renderizar cards (única fuente del template)
    items = []
    dailyplan_meals = dailyplan.meals_with_foods()

    for dpm in dailyplan_meals:
        items.append({
            "meal": dpm.meal,
            "daily_plan_meal": dpm,

            # 👇 NUEVO: URL construida por routing helper
            "meal_url": meal_url(
                dpm.meal,
                dailyplan=dailyplan,
            ),

    "actions": (
        resolve_meal_actions(
            dpm.meal,
            request.user,
            context={
                "context": MEAL_CONTEXT_DAILYPLAN,
                "dailyplan": dailyplan,
            },
        )
        + resolve_dailyplan_meal_actions(dpm, request.user)
    ),
})


    navigation = [
        {"label": "Daily Plans", "url": reverse("dailyplan_list")},
        {"label": dailyplan.name, "url": None},
    ]


    return render(
        request,
        "notas/dailyplans/detail.html",
        {
            "dailyplan": dailyplan,
            "meals": meals,   # selector Add meal
            "dailyplan_meals": dailyplan_meals,
            "items": items,   # cards
            "navigation": navigation,
        },
    )



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

        return redirect("dailyplan_detail", pk=dailyplan.pk)

    return render(request, "notas/dailyplans/create.html")


@login_required
def remove_meal(request, dailyplan_id, item_id):
    item = get_object_or_404(
        DailyPlanMeal,
        pk=item_id,
        daily_plan_id=dailyplan_id,
    )

    dailyplan_id = item.daily_plan.id
    item.delete()

    return redirect("dailyplan_detail", pk=dailyplan_id)


@require_POST
def add_meal_to_dailyplan(request, pk):
    dailyplan = get_object_or_404(DailyPlan, pk=pk)

    meal_id = request.POST.get("meal_id")
    note = request.POST.get("note","").strip() or None
    hour = request.POST.get("hour") or None  # 👈 CLAVE

    if not meal_id:
        messages.error(request, "Meal y título son obligatorios")
        return redirect("dailyplan_detail", pk=dailyplan.pk)

    meal = get_object_or_404(Meal, pk=meal_id)

    DailyPlanMeal.objects.create(
        daily_plan=dailyplan,
        meal=meal,
        note=note or None,
        hour=hour or None
    )

    messages.success(request, "Meal agregada al daily plan")
    return redirect("dailyplan_detail", pk=dailyplan.pk)


@login_required
def configure_dailyplan(request, pk):

    dailyplan = get_object_or_404(DailyPlan, pk=pk)

    if dailyplan.created_by != request.user:
        messages.error(request, "You cannot configure this daily plan.")
        return redirect("dailyplan_detail", pk=pk)

    profile = request.user.profile

    if request.method == "POST":
        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        # Aplicar reglas de permisos (helpers mandan)
        if not can_publish(profile):
            is_public = False

        if not can_fork(profile):
            is_forkable = False

        if not can_copy(profile):
            is_copiable = False

        dailyplan.is_public = is_public
        dailyplan.is_forkable = is_forkable
        dailyplan.is_copiable = is_copiable

        if dailyplan.is_draft:
            if not dailyplan.daily_plan_meals.exists():
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
            "profile": profile,
            "can_publish": can_publish(profile),
            "can_fork": can_fork(profile),
            "can_copy": can_copy(profile),
        }
    )


@login_required
def attach_meal_to_dailyplan(request, dailyplan_id, meal_id):
    dailyplan = get_object_or_404(DailyPlan, id=dailyplan_id)
    meal = get_object_or_404(Meal, id=meal_id)

    if request.method == "POST":
        hour = request.POST.get("hour")
        note = request.POST.get("note")

        DailyPlanMeal.objects.create(
            daily_plan=dailyplan,
            meal=meal,
            hour=hour or None,
            note=note or None
        )

        return redirect("dailyplan_detail", pk=dailyplan.id)

    return render(
        request,
        "notas/dailyplans/attach_meal.html",
        {
            "dailyplan": dailyplan,
            "meal": meal
        }
    )
































