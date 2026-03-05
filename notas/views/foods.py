import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from openpyxl import Workbook
from django.contrib import messages
from notas.services.capabilities import get_capabilities
from notas.models import Food
from notas.actions.constants import (
    FOOD_VIEWMODE_PERSONAL_LIST, 
    FOOD_VIEWMODE_PERSONAL_DETAIL,
    FOOD_VIEWMODE_PERSONAL_EDIT,
)
from notas.routing.food import food_url
from notas.viewmodels.content.builder.list_foods_builder import build_food_list_vm
from notas.viewmodels.content.builder.detail_food_builder import build_food_detail_vm
from notas.viewmodels.content.builder.edit_food_builder import build_food_edit_vm

from notas.services.food import create_food

from notas.viewmodels.base_vm import BaseVM
from notas.viewmodels.ui.builder_ui import build_ui_vm

#************ RENDER COMPLEJOS *********************
# ---------- LIST - DETAIL ----------
@login_required
def food_list(request):

    foods = Food.objects.filter(created_by=request.user).order_by("name")

    viewmode = FOOD_VIEWMODE_PERSONAL_LIST

    ui_vm = build_ui_vm(viewmode)

    content_vm = build_food_list_vm(
        foods,
        request.user,
        viewmode,
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/foods/list.html",
        base_vm.as_context(),
    )



def food_detail(request, pk):

    food = get_object_or_404(Food, pk=pk)

    viewmode = FOOD_VIEWMODE_PERSONAL_DETAIL


    content_vm = build_food_detail_vm(
        food,
        request.user,
        viewmode,
    )

    ui_vm = build_ui_vm(viewmode, instance=food)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/foods/detail.html",
        base_vm.as_context(),
    )


def food_edit(request, pk):

    food = get_object_or_404(Food, pk=pk)
    print("POST DATA:", request.POST)
    if request.method == "POST":

        food.name = request.POST.get("name")
        food.protein = float(request.POST.get("protein"))
        food.carbs = float(request.POST.get("carbs"))
        food.fat = float(request.POST.get("fat"))

        food.save()

        return redirect("food_detail", pk=food.pk)

    viewmode = FOOD_VIEWMODE_PERSONAL_EDIT

    content_vm = build_food_edit_vm(food)

    ui_vm = build_ui_vm(viewmode, instance=food)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/foods/edit.html",
        base_vm.as_context(),
    )




#************ RENDER BÁSICOS *********************
# ---------- CREATE - *FALTA_RENAME - CONFIGURE ----------

def food_create(request):

    if request.method == "POST":

        name = request.POST.get("name")
        protein = float(request.POST.get("protein"))
        carbs = float(request.POST.get("carbs"))
        fat = float(request.POST.get("fat"))

        create_food(
            user=request.user,
            name=name,
            protein=protein,
            carbs=carbs,
            fat=fat
        )

        return redirect("food_list")

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




