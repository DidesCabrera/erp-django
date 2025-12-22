import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from notas.models import Food
from django.http import HttpResponse
from openpyxl import Workbook



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


@login_required
def food_list(request):
    foods = Food.objects.filter(created_by=request.user).order_by("name")

    return render(
        request,
        "notas/foods/list.html",
        {"foods": foods}
    )




