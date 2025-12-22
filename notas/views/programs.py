from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from notas.models import Program, ProgramDay, DailyPlan
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from notas.services.permissions import can_copy
from django.contrib import messages
from datetime import date



@login_required
@require_POST
def fork_program(request, program_id):
    original = get_object_or_404(Program, id=program_id)

    with transaction.atomic():
        forked = Program.objects.create(
            name=f"{original.name} (fork)",
            created_by=request.user,
            original_author=original.created_by,
            forked_from=original,
            start_date=original.start_date,
            end_date=original.end_date,
            is_public=False
        )

        for day in original.program_days.all():
            ProgramDay.objects.create(
                program=forked,
                daily_plan=day.daily_plan,
                date=day.date
            )

    return redirect('program_detail', forked.id)


@login_required
@require_POST
def copy_program(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if not can_copy(request.user, program):
        return HttpResponseForbidden("No puedes copiar este programa")

    copy = Program.objects.create(
        name=f"{program.name} (copy)",
        created_by=request.user,
        start_date=program.start_date,
        end_date=program.end_date,
        is_public=False,
        is_forkable=True,
        is_copiable=False,
    )

    # copiar los días del programa
    for day in program.program_days.all():
        ProgramDay.objects.create(
            program=copy,
            daily_plan=day.daily_plan,
            date=day.date,
        )

    return redirect("program_detail", pk=copy.pk)


@login_required
def program_list(request):
    programs = Program.objects.filter(created_by=request.user).order_by("-created_at")

    return render(
        request,
        "notas/programs/list.html",
        {"programs": programs}
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

        # Regla de negocio por plan
        if profile.role == "member":
            max_days = profile.plan.max_program_duration_days

            if max_days and duration_days > max_days:
                messages.error(
                    request,
                    f"Tu plan permite programas de hasta {max_days} días."
                )
                return redirect("program_create")

        # Crear el programa
        program = Program.objects.create(
            name=name,
            created_by=request.user,
            start_date=start_date,
            end_date=end_date
        )

        return redirect("program_detail", pk=program.pk)

    return render(request, "notas/programs/create.html")



def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk)

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
        daily_plan=dailyplan,
        date=date
    )

    messages.success(request, "Daily plan agregado al programa")
    return redirect("program_detail", pk=program.pk)


@login_required
def configure_program(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if program.created_by != request.user:
        messages.error(request, "You cannot configure this program.")
        return redirect("program_detail", pk=pk)
    
    profile = request.user.profile

    if request.method == "POST":
        is_public = bool(request.POST.get("is_public"))
        is_forkable = bool(request.POST.get("is_forkable"))
        is_copiable = bool(request.POST.get("is_copiable"))

        if profile.role == "member":
            is_public = False
            is_forkable = True
            is_copiable = False

        program.is_public = is_public
        program.is_forkable = is_forkable
        program.is_copiable = is_copiable

        if program.is_draft:
            if not program.program_days.exists():
                messages.error(request, "Add at least one day before finalizing.")
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
            "profile": request.user.profile
        }
    )



















