from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notas.models import Program, ProgramDay, DailyPlan
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from datetime import date
from notas.services.capabilities import get_capabilities
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from notas.services.nutrition import (
    PROTEIN_KCAL_PER_GRAM,
    CARBS_KCAL_PER_GRAM,
    FAT_KCAL_PER_GRAM,
)




@login_required
@require_POST
def fork_program(request, program_id):
    original = get_object_or_404(
        Program.objects.prefetch_related("program_dailyplan__dailyplan"),
        id=program_id,
    )

    with transaction.atomic():
        forked = Program.objects.create(
            name=f"{original.name} (fork)",
            created_by=request.user,
            original_author=original.created_by,
            forked_from=original,
            start_date=original.start_date,
            end_date=original.end_date,
            is_public=False,
        )

        for day in original.program_dailyplan.all():
            ProgramDay.objects.create(
                program=forked,
                dailyplan=day.dailyplan,
                date=day.date,
            )

    return redirect("program_detail", forked.id)


@login_required
@require_POST
def copy_program(request, pk):
    program = get_object_or_404(
        Program.objects.prefetch_related("program_dailyplan__dailyplan"),
        pk=pk,
    )

    copy = Program.objects.create(
        name=f"{program.name} (copy)",
        created_by=request.user,
        start_date=program.start_date,
        end_date=program.end_date,
        is_public=False,
        is_forkable=True,
        is_copiable=False,
    )

    for day in program.program_dailyplan.all():
        ProgramDay.objects.create(
            program=copy,
            dailyplan=day.dailyplan,
            date=day.date,
        )

    return redirect("program_detail", pk=copy.pk)


@login_required
def program_list(request):

    programs = (
        Program.objects
        .filter(created_by=request.user)
        .order_by("-created_at")
        .prefetch_related(
            "program_dailyplan__dailyplan__dailyplan_meals__meal__meal_food_set__food"
        )
        .annotate(
            total_kcal_sql=Sum(
                ExpressionWrapper(
                    (F("program_dailyplan__dailyplan__dailyplan_meals__meal__meal_food_set__quantity") / 100.0) * (
                        F("program_dailyplan__dailyplan__dailyplan_meals__meal__meal_food_set__food__protein") * PROTEIN_KCAL_PER_GRAM +
                        F("program_dailyplan__dailyplan__dailyplan_meals__meal__meal_food_set__food__carbs")   * CARBS_KCAL_PER_GRAM +
                        F("program_dailyplan__dailyplan__dailyplan_meals__meal__meal_food_set__food__fat")     * FAT_KCAL_PER_GRAM
                    ),
                    output_field=FloatField(),
                )
            )
        )
    )


    return render(
        request,
        "notas/programs/list.html",
        {"programs": programs},
    )



@login_required
def program_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        if not all([name, start_date_str, end_date_str]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("program_create")

        # Convertir strings a date
        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            messages.error(request, "Fechas inválidas.")
            return redirect("program_create")

        if end_date < start_date:
            messages.error(request, "La fecha de término no puede ser anterior a la de inicio.")
            return redirect("program_create")

        # Calcular duración
        duration_days = (end_date - start_date).days + 1

        profile = request.user.profile

        # Crear el programa
        program = Program.objects.create(
            name=name,
            created_by=request.user,
            start_date=start_date,
            end_date=end_date
        )

        return redirect("program_detail", pk=program.pk)

    return render(request, "notas/programs/create.html")



@login_required
def program_detail(request, pk):

    program = get_object_or_404(
        Program.objects.prefetch_related(
            "program_dailyplan__dailyplan__dailyplan_meals__meal__meal_food_set__food"
        ),
        pk=pk,
    )

    dailyplans = DailyPlan.objects.filter(created_by=request.user)

    return render(
        request,
        "notas/programs/detail.html",
        {
            "program": program,
            "dailyplans": dailyplans,
        }
    )



@require_POST
def add_dailyplan_to_program(request, pk):
    program = get_object_or_404(Program, pk=pk)

    dailyplan_id = request.POST.get("dailyplan_id")
    date = request.POST.get("date")

    if not dailyplan_id or not date:
        messages.error(request, "Daily plan y fecha son obligatorios")
        return redirect("program_detail", pk=program.pk)

    dailyplan = get_object_or_404(DailyPlan, pk=dailyplan_id)

    ProgramDay.objects.create(
        program=program,
        dailyplan=dailyplan,
        date=date
    )

    messages.success(request, "Daily plan agregado al programa")
    return redirect("program_detail", pk=program.pk)


@login_required
def configure_program(request, pk):

    program = get_object_or_404(
        Program.objects.prefetch_related("program_dailyplan"),
        pk=pk,
        created_by=request.user,
    )

    caps = get_capabilities(request.user)

    if request.method == "POST":
        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        if is_public and not caps.can_publish():
            messages.error(request, "You cannot publish this program.")
            return redirect("configure_program", pk=pk)

        if is_copiable and not caps.can_copy():
            messages.error(request, "Your plan does not allow copies.")
            return redirect("configure_program", pk=pk)

        program.is_public = is_public
        program.is_forkable = is_forkable
        program.is_copiable = is_copiable

        if program.is_draft:
            if not program.program_dailyplan.exists():
                messages.error(
                    request,
                    "Add at least one day before finalizing."
                )
                return redirect("program_detail", pk=pk)

            program.is_draft = False

        program.save()
        messages.success(request, "Program saved.")
        return redirect("program_detail", pk=pk)

    return render(
        request,
        "notas/programs/configure.html",
        {
            "program": program,
            "caps": caps,
        }
    )



















