from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.contrib import messages
from notas.actions.meal_resolvers import resolve_meal_actions
from notas.models import Meal, MealFood, DailyPlan, DailyPlanMeal, Food
from notas.services.permissions import can_fork, can_copy, can_publish
from django.urls import reverse
from notas.actions.constants import MEAL_CONTEXT_LIST


# ==================================================
# FORK MEAL
# ==================================================

@login_required
@require_POST
def fork_meal(request, meal_id):
    original_meal = get_object_or_404(Meal, id=meal_id)
    profile = request.user.profile

    if not can_fork(profile) or not original_meal.is_forkable:
        return HttpResponseForbidden("No puedes forkear esta meal")

    original_author = (
        original_meal.original_author
        if original_meal.original_author
        else original_meal.created_by
    )

    forked_meal = Meal.objects.create(
        name=f"{original_meal.name} (fork)",
        created_by=request.user,
        original_author=original_author,
        forked_from=original_meal,
        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    MealFood.objects.bulk_create([
        MealFood(
            meal=forked_meal,
            food=mf.food,
            quantity=mf.quantity
        )
        for mf in original_meal.mealfood_set.all()
    ])

    messages.success(request, "Meal forked successfully")
    return redirect("meal_detail", pk=forked_meal.pk)


# ==================================================
# REPLACE MEAL IN DAILY PLAN
# ==================================================

@login_required
def replace_meal(request, daily_plan_meal_id, new_meal_id):
    daily_plan_meal = get_object_or_404(DailyPlanMeal, id=daily_plan_meal_id)
    new_meal = get_object_or_404(Meal, id=new_meal_id)

    if daily_plan_meal.daily_plan.created_by != request.user:
        return redirect("dailyplan_detail", daily_plan_meal.daily_plan.id)

    daily_plan_meal.meal = new_meal
    daily_plan_meal.save()

    return redirect("dailyplan_detail", daily_plan_meal.daily_plan.id)


# ==================================================
# COPY MEAL
# ==================================================

@login_required
@require_POST
def copy_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk)
    profile = request.user.profile

    if not can_copy(profile) or not meal.is_copiable:
        return HttpResponseForbidden("No tienes permiso para copiar esta meal")

    copy = Meal.objects.create(
        name=f"{meal.name} (copy)",
        created_by=request.user,
        is_public=False,
        is_forkable=True,
        is_copiable=False,
        is_draft=False,
    )

    for mf in meal.mealfood_set.all():
        MealFood.objects.create(
            meal=copy,
            food=mf.food,
            quantity=mf.quantity
        )

    messages.success(request, "Meal copiada correctamente")
    return redirect("meal_detail", pk=copy.pk)


# ==================================================
# LIST / DETAIL
# ==================================================

@login_required
def meal_list(request):
    meals = Meal.objects.filter(
        created_by=request.user,
        is_draft=False
    ).order_by("-created_at")

    items = []

    for meal in meals:
        items.append({
            "meal": meal,
            "actions": resolve_meal_actions(
                meal,
                request.user,
                context={
                    "context": MEAL_CONTEXT_LIST,
                },
            ),
        })

    return render(
        request, 
        "notas/meals/list.html", 
        {
        "items": items,
    })



def meal_detail(request, pk, dailyplan_id=None):
    meal = get_object_or_404(Meal, pk=pk, created_by=request.user)
    foods = Food.objects.all()

    actions = resolve_meal_actions(meal, user=request.user)
    
    navigation = []

    # 👉 CASO 1: entro desde un DailyPlan
    if dailyplan_id:
        dailyplan = get_object_or_404(
            DailyPlan,
            pk=dailyplan_id,
            created_by=request.user,
        )

        navigation = [
            {"label": "Daily Plans", "url": reverse("dailyplan_list")},
            {
                "label": dailyplan.name,
                "url": dailyplan.get_absolute_url(),
            },
            {"label": meal.name, "url": None},
        ]

    # 👉 CASO 2: entro directo a la Meal
    else:
        navigation = [
            {"label": "Meals", "url": reverse("meal_list")},
            {"label": meal.name, "url": None},
        ]

    return render(
        request,
        "notas/meals/detail.html",
        {
            "meal": meal,
            "foods": foods,
            "actions": actions,
            "navigation": navigation,
        },
    )




# ==================================================
# CREATE / ADD FOOD
# ==================================================

@login_required
def meal_create(request):
    from_dailyplan = request.GET.get("from_dailyplan")

    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "El nombre es obligatorio")
            return redirect("meal_create")

        meal = Meal.objects.create(
            name=name,
            created_by=request.user,
            is_draft=True
        )

        if from_dailyplan:
            return redirect(
                "attach_meal_to_dailyplan",
                dailyplan_id=from_dailyplan,
                meal_id=meal.id
            )

        return redirect("meal_detail", pk=meal.pk)

    return render(request, "notas/meals/create.html")


@require_POST
def add_food_to_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk)

    food_id = request.POST.get("food_id")
    quantity = request.POST.get("quantity")

    if not food_id or not quantity:
        messages.error(request, "Food y cantidad son obligatorios")
        return redirect("meal_detail", pk=meal.pk)

    food = get_object_or_404(Food, pk=food_id)

    MealFood.objects.create(
        meal=meal,
        food=food,
        quantity=quantity
    )

    messages.success(request, "Food agregado a la meal")
    return redirect("meal_detail", pk=meal.pk)


# ==================================================
# CONFIGURE MEAL
# ==================================================

@login_required
def configure_meal(request, pk):
    meal = get_object_or_404(Meal, pk=pk)
    profile = request.user.profile

    if meal.created_by != request.user:
        messages.error(request, "You cannot configure this meal.")
        return redirect("meal_detail", pk=meal.pk)

    if not meal.is_draft:
        messages.info(request, "This meal is already finalized.")
        return redirect("meal_detail", pk=meal.pk)

    if request.method == "POST":
        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        if not can_publish(profile):
            is_public = False

        if not can_fork(profile):
            is_forkable = False

        if not can_copy(profile):
            is_copiable = False

        meal.is_public = is_public
        meal.is_forkable = is_forkable
        meal.is_copiable = is_copiable
        meal.is_draft = False
        meal.save()

        messages.success(request, "Meal creada successfully.")
        return redirect("meal_detail", pk=meal.pk)

    return render(
        request,
        "notas/meals/configure.html",
        {
            "meal": meal,
            "profile": profile,
            "can_publish": can_publish(profile),
            "can_fork": can_fork(profile),
            "can_copy": can_copy(profile),
        }
    )
