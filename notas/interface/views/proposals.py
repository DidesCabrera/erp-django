from dataclasses import dataclass

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from notas.application.queries.proposal_queries import (
    get_available_proposal_queryset,
    get_proposal_detail,
    list_user_proposals,
)
from notas.application.services.commands.proposal_commands import (
    approve_proposal,
    cancel_proposal,
    reject_proposal,
    apply_approved_create_dailyplan_proposal,
    apply_approved_create_meal_proposal,
)
from notas.application.dto.proposal_payloads import (
    CREATE_DAILYPLAN_INTENT,
    CREATE_MEAL_INTENT,
)
from notas.presentation.composition.viewmodel.components.builder_headers import (
    build_page_header,
)
from notas.presentation.composition.viewmodel.ui_builder import build_ui_vm
from notas.presentation.config.viewmodel_config import (
    PROPOSAL_VIEWMODE_DETAIL,
    PROPOSAL_VIEWMODE_LIST,
)
from notas.presentation.viewmodels.base_vm import BaseVM

from notas.presentation.proposals.proposal_review_viewmodels import (
    build_proposal_review_vm,
)

@dataclass
class ProposalListContentVM:
    header: object
    proposals: list[dict]


@dataclass
class ProposalDetailContentVM:
    header: object
    proposal: dict
    proposal_review: dict


@dataclass(frozen=True)
class BreadcrumbParent:
    label: str
    url: str

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return self.url


def _proposal_list_parent():
    return BreadcrumbParent(
        label="Propuestas",
        url=reverse("proposal_list"),
    )


def _get_proposal_model_for_action(user, proposal_id: int):
    return get_object_or_404(
        get_available_proposal_queryset(user),
        pk=proposal_id,
    )


def _build_detail_actions(proposal: dict):
    if not proposal["is_reviewable"]:
        return []

    return [
        {
            "key": "approve",
            "label": "Aprobar propuesta",
            "url": reverse("proposal_approve", args=[proposal["id"]]),
            "method": "post",
            "icon": "check",
            "order": 10,
            "desktop_position": "inline",
            "mobile_position": "inline",
        },
        {
            "key": "reject",
            "label": "Rechazar propuesta",
            "url": reverse("proposal_reject", args=[proposal["id"]]),
            "method": "post",
            "icon": "x",
            "order": 20,
            "desktop_position": "inline",
            "mobile_position": "inline",
        },
        {
            "key": "cancel",
            "label": "Cancelar propuesta",
            "url": reverse("proposal_cancel", args=[proposal["id"]]),
            "method": "post",
            "icon": "ban",
            "order": 30,
            "desktop_position": "menu",
            "mobile_position": "menu",
        },
    ]


def _get_proposal_intent(proposal):
    payload = proposal.proposed_payload

    if not isinstance(payload, dict):
        return None

    intent = payload.get("intent")

    if isinstance(intent, str) and intent.strip():
        return intent.strip()

    return None


@login_required
def proposal_list(request):
    proposals = [
        proposal.as_dict()
        for proposal in list_user_proposals(request.user)
    ]

    content_vm = ProposalListContentVM(
        header=build_page_header(
            title="Propuestas",
        ),
        proposals=proposals,
    )

    ui_vm = build_ui_vm(PROPOSAL_VIEWMODE_LIST)

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/proposals/list.html",
        base_vm.as_context(),
    )


@login_required
def proposal_detail(request, proposal_id):
    proposal = get_proposal_detail(
        request.user,
        proposal_id,
    ).as_dict()

    proposal_review = build_proposal_review_vm(
        proposal,
    ).as_dict()

    content_vm = ProposalDetailContentVM(
        header=build_page_header(
            title=proposal["title"],
            actions=_build_detail_actions(proposal),
        ),
        proposal=proposal,
        proposal_review=proposal_review,
    )

    ui_vm = build_ui_vm(
        PROPOSAL_VIEWMODE_DETAIL,
        parents=[
            _proposal_list_parent(),
        ],
        instance=proposal["title"],
        back_config={
            "type": "parent",
        },
    )

    base_vm = BaseVM(
        ui=ui_vm,
        content=content_vm,
    )

    return render(
        request,
        "notas/proposals/detail.html",
        base_vm.as_context(),
    )


@login_required
@require_POST
def proposal_approve(request, proposal_id):
    proposal = _get_proposal_model_for_action(
        request.user,
        proposal_id,
    )

    approve_proposal(
        user=request.user,
        proposal=proposal,
    )

    messages.success(request, "Propuesta aprobada.")

    return redirect(
        "proposal_detail",
        proposal_id=proposal.id,
    )


@login_required
@require_POST
def proposal_reject(request, proposal_id):
    proposal = _get_proposal_model_for_action(
        request.user,
        proposal_id,
    )

    reject_proposal(
        user=request.user,
        proposal=proposal,
    )

    messages.success(request, "Propuesta rechazada.")

    return redirect(
        "proposal_detail",
        proposal_id=proposal.id,
    )


@login_required
@require_POST
def proposal_cancel(request, proposal_id):
    proposal = _get_proposal_model_for_action(
        request.user,
        proposal_id,
    )

    cancel_proposal(
        user=request.user,
        proposal=proposal,
    )

    messages.success(request, "Propuesta cancelada.")

    return redirect(
        "proposal_detail",
        proposal_id=proposal.id,
    )


@login_required
def proposal_apply(request, proposal_id):
    if request.method != "POST":
        return redirect(
            "proposal_detail",
            proposal_id=proposal_id,
        )

    proposal = _get_proposal_model_for_action(
        request.user,
        proposal_id,
    )

    intent = _get_proposal_intent(proposal)

    try:
        if intent == CREATE_MEAL_INTENT:
            result = apply_approved_create_meal_proposal(
                user=request.user,
                proposal=proposal,
            )

            messages.success(
                request,
                f'Propuesta aplicada. Comida creada: "{result.meal.name}".',
            )

        elif intent == CREATE_DAILYPLAN_INTENT:
            result = apply_approved_create_dailyplan_proposal(
                user=request.user,
                proposal=proposal,
            )

            messages.success(
                request,
                f'Propuesta aplicada. DailyPlan creado: "{result.dailyplan.name}".',
            )

        else:
            messages.error(
                request,
                "Esta propuesta no tiene un tipo aplicable.",
            )

    except ValueError as exc:
        messages.error(
            request,
            f"No se pudo aplicar la propuesta: {exc}",
        )

    return redirect(
        "proposal_detail",
        proposal_id=proposal_id,
    )