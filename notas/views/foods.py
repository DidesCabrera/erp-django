import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from openpyxl import Workbook
from django.contrib import messages
from notas.services.capabilities import get_capabilities
from notas.actions.food_resolvers import resolve_food_actions
from notas.models import Meal, Food
from django.urls import reverse
from notas.actions.constants import (
    FOOD_VIEWMODE_LIST, 
    FOOD_VIEWMODE_DETAIL,
    FOOD_VIEWMODE_EDIT,
)
from notas.routing.food import food_url
from notas.viewmodels.content.builder.list_foods_builder import build_food_list_vm






#************ RENDER COMPLEJOS *********************
# ---------- LIST - DETAIL ----------
@login_required
def food_list(request):
    foods = Food.objects.filter(created_by=request.user).order_by("name")

    vm = build_food_list_vm(
        foods,
        request.user,
        FOOD_VIEWMODE_LIST,
    )

    items = []
    for food in foods:
        items.append({
            "obj": food,
            "url": food_url(food),
            "actions": resolve_food_actions(
                food,
                request.user,
                context={
                    "name": FOOD_VIEWMODE_LIST,
                },
            ),
        })

    return render(
        request,
        "notas/foods/list.html",
        {
            "foods": foods,
            "items": items, 
            "vm": vm,
        }
    )

@login_required
def food_detail(request, pk, food_id=None):
    food = get_object_or_404(
        Food,
        pk=pk,
        created_by=request.user,
    )

    caps = get_capabilities(request.user)
    if not caps:
        return HttpResponseForbidden("Unauthorized")

    foods = Food.objects.all()

    # --------------------------------------------------
    # ACTIONS – food (header / card principal)
    # --------------------------------------------------

    item = {
        "food": food,
        "actions": resolve_food_actions(
                food,
                request.user,
                context={
                    "name": FOOD_VIEWMODE_DETAIL
                },
            ),
    }


    # --------------------------------------------------
    # NAVIGATION / HEADER
    # --------------------------------------------------

    navigation = [
        {"label": "My Foods","url": reverse("food_list")},
        {"label": food.name,"url": None},
    ]

    header = {
        "title": food.name,
        "subtitle": f"{food.total_kcal:.0f} kcal",
        "navigation": navigation,
        "actions": resolve_food_actions(
                food,
                request.user,
                context={
                    "name": FOOD_VIEWMODE_DETAIL
                },
            ),
    }

    # --------------------------------------------------
    # RENDER
    # --------------------------------------------------

    return render(
        request,
        "notas/foods/detail.html",
        {
            "food": food,               
            "item": item,          
            "navigation": navigation,
            "header": header,
        },
        
    )


# ---------- EDIT - BUILDER ----------
@login_required
def food_edit(request, pk):
    food = get_object_or_404(Food, pk=pk)

    foods = Food.objects.all()

    caps = get_capabilities(request.user)

    if not caps or not caps.can_edit_own_content():
        return HttpResponseForbidden("You cannot edit this food")

    # --------------------------------------------------
    # NAVIGATION / HEADER
    # --------------------------------------------------

    navigation = [
        {"label": "Foods","url": reverse("food_list")},
        {"label": food.name,"url": None},
    ]

    header = {
        "title": food.name,
        "subtitle": f"{food.total_kcal:.0f} kcal",
        "navigation": navigation,
        "actions": resolve_food_actions(
                food,
                request.user,
                context={
                    "name": FOOD_VIEWMODE_EDIT
                },
            ),
    }


    return render(
        request,
        "notas/foods/edit.html",
        {
            "food": food,
            "header": header,
        }
    )


#************ RENDER BÁSICOS *********************
# ---------- CREATE - *FALTA_RENAME - CONFIGURE ----------

@login_required
def food_create(request):

    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "El nombre es obligatorio")
            return redirect("food_create")

        food = Food.objects.create(
            name=name,
            created_by=request.user,
            is_draft=True
        )

        return redirect("food_edit", pk=food.pk)

    return render(request, "notas/foods/create.html")


@login_required
def food_configure(request, pk):
    food = get_object_or_404(
        Food,
        pk=pk,
    )

    caps = get_capabilities(request.user)

    if request.method == "POST":
        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        # ---- reglas de negocio ----
        if is_public and not caps.can_publish():
            messages.error(request, "You cannot publish this food.")
            return redirect("food_configure", pk=pk)

        if is_copiable and not caps.can_copy():
            messages.error(request, "Your plan does not allow copies.")
            return redirect("food_configure", pk=pk)

        food.is_public = is_public
        food.is_forkable = is_forkable
        food.is_copiable = is_copiable

        food.save()
        messages.success(request, "Food saved.")
        return redirect("food_detail", pk=pk)

    return render(
        request,
        "notas/foods/configure.html",
        {
            "food": food,
            "caps": caps,
        }
    )


@login_required
def import_foods(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            messages.error(request, "Please upload a file.")
            return redirect("import_foods")

        try:
            df = pd.read_excel(file)

            required_columns = {"name", "protein", "carbs", "fat"}
            if not required_columns.issubset(df.columns):
                messages.error(
                    request,
                    f"Missing columns. Required: {', '.join(required_columns)}"
                )
                return redirect("import_foods")

            created = 0

            for _, row in df.iterrows():
                Food.objects.create(
                    name=row["name"],
                    protein=row["protein"],
                    carbs=row["carbs"],
                    fat=row["fat"],
                    created_by=request.user
                )
                created += 1

            messages.success(request, f"{created} foods imported successfully.")

        except Exception as e:
            messages.error(request, f"Import failed: {e}")

        return redirect("food_list")

    return render(request, "notas/foods/import.html")


@login_required
def download_food_template(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Foods"

    # Headers
    ws.append([
        "name",
        "protein",
        "carbs",
        "fat",
    ])

    # Optional example row (muy útil)
    ws.append([
        "Chicken breast",
        31,
        0,
        3.6,
    ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="food_import_template.xlsx"'

    wb.save(response)
    return response



def foods_json(request):
    foods = []

    for food in Food.objects.all().order_by("name"):
        foods.append({
            "id": food.id,
            "name": food.name,
            "protein": food.protein,
            "carbs": food.carbs,
            "fat": food.fat,
            "total_kcal": food.total_kcal,
            "alloc": food.alloc,
        })

    return JsonResponse(foods, safe=False)




