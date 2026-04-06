from dataclasses import dataclass
from typing import List, Optional

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from notas.domain.models import DailyPlan, Meal, Food, WeightLog
from notas.presentation.config.viewmodel_config import PROFILE_VIEWMODE
from notas.presentation.viewmodels.base_vm import BaseVM
from notas.presentation.composition.viewmodel.ui_builder import build_ui_vm
from notas.application.services.nutrition.weight import get_current_weight


@dataclass
class ProfileStatVM:
    label: str
    value: str
    icon: str


@dataclass
class ProfileWeightEntryVM:
    date: str
    weight: float


@dataclass
class ProfileActionVM:
    label: str
    url: str
    icon: str


@dataclass
class ProfileContentVM:
    title: str
    subtitle: str
    stats: List[ProfileStatVM]
    weight_current: Optional[float]
    weight_updated_at: Optional[str]
    weight_history: List[ProfileWeightEntryVM]
    actions: List[ProfileActionVM]


@login_required
def profile_detail(request):
    user = request.user
    profile = user.profile

    current_weight = get_current_weight(user)
    weight_logs = list(user.weight_logs.all()[:5])
    last_weight_log = weight_logs[0] if weight_logs else None

    content = ProfileContentVM(
        title=f"{user.username}",
        subtitle=(
            "Gestiona tu información de cuenta y el peso corporal usado "
            "como referencia para el cálculo de proteína por kilo."
        ),
        stats=[
            ProfileStatVM(
                label="Rol",
                value=profile.get_role_display(),
                icon="badge-check",
            ),
            ProfileStatVM(
                label="Plan",
                value=profile.plan.name if profile.plan else "Sin plan",
                icon="credit-card",
            ),
            ProfileStatVM(
                label="Peso actual",
                value=f"{current_weight:.1f} kg" if current_weight else "Sin registro",
                icon="scale",
            ),
        ],
        weight_current=current_weight,
        weight_updated_at=(
            last_weight_log.date.strftime("%Y-%m-%d")
            if last_weight_log else None
        ),
        weight_history=[
            ProfileWeightEntryVM(
                date=log.date.strftime("%Y-%m-%d"),
                weight=log.weight_kg,
            )
            for log in weight_logs
        ],
        actions=[
            ProfileActionVM(
                label="Ver DailyPlans",
                url=reverse("dailyplan_list"),
                icon="clipboard-list",
            ),
            ProfileActionVM(
                label="Ver Meals",
                url=reverse("meal_list"),
                icon="salad",
            ),
            ProfileActionVM(
                label="Ver Foods",
                url=reverse("food_list"),
                icon="carrot",
            ),
        ],
    )

    ui = build_ui_vm(PROFILE_VIEWMODE)

    vm = BaseVM(
        ui=ui,
        content=content,
    )

    context = vm.as_context()
    context["profile"] = profile

    return render(
        request,
        "notas/profile/detail.html",
        context,
    )