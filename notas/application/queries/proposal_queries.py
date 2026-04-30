from django.db.models import Q
from django.shortcuts import get_object_or_404

from notas.application.dto.proposal_dto import (
    NutritionProposalDTO,
    NutritionProposalListItemDTO,
)
from notas.domain.models import NutritionProposal


def _serialize_datetime(value):
    if value is None:
        return None

    return value.isoformat()


def get_available_proposal_queryset(user):
    """
    Propuestas visibles para el usuario.

    Regla inicial conservadora:
    - propuestas creadas por el usuario;
    - propuestas asociadas a DailyPlans propios del usuario.

    No se incluyen todavía propuestas de DailyPlans compartidos, porque eso
    requiere una decisión de producto más fina sobre permisos de revisión.
    """
    return (
        NutritionProposal.objects
        .select_related(
            "dailyplan",
            "created_by",
            "reviewed_by",
        )
        .filter(
            Q(created_by=user)
            | Q(dailyplan__created_by=user)
        )
        .distinct()
        .order_by("-created_at", "-id")
    )


def build_proposal_list_item_dto(
    proposal: NutritionProposal,
) -> NutritionProposalListItemDTO:
    return NutritionProposalListItemDTO(
        id=proposal.id,
        dailyplan_id=proposal.dailyplan_id,
        dailyplan_name=proposal.dailyplan.name,
        created_by_id=proposal.created_by_id,
        created_by_username=proposal.created_by.username,
        reviewed_by_id=proposal.reviewed_by_id,
        reviewed_by_username=(
            proposal.reviewed_by.username
            if proposal.reviewed_by
            else None
        ),
        status=proposal.status,
        source=proposal.source,
        title=proposal.title,
        summary=proposal.summary,
        is_reviewable=proposal.is_reviewable,
        is_final=proposal.is_final,
        created_at=_serialize_datetime(proposal.created_at),
        reviewed_at=_serialize_datetime(proposal.reviewed_at),
    )


def build_proposal_dto(
    proposal: NutritionProposal,
) -> NutritionProposalDTO:
    return NutritionProposalDTO(
        id=proposal.id,
        dailyplan_id=proposal.dailyplan_id,
        dailyplan_name=proposal.dailyplan.name,
        created_by_id=proposal.created_by_id,
        created_by_username=proposal.created_by.username,
        reviewed_by_id=proposal.reviewed_by_id,
        reviewed_by_username=(
            proposal.reviewed_by.username
            if proposal.reviewed_by
            else None
        ),
        status=proposal.status,
        source=proposal.source,
        title=proposal.title,
        summary=proposal.summary,
        targets=proposal.targets or {},
        current_snapshot=proposal.current_snapshot or {},
        proposed_payload=proposal.proposed_payload or {},
        validation_summary=proposal.validation_summary or {},
        is_reviewable=proposal.is_reviewable,
        is_final=proposal.is_final,
        created_at=_serialize_datetime(proposal.created_at),
        reviewed_at=_serialize_datetime(proposal.reviewed_at),
    )


def list_user_proposals(user) -> list[NutritionProposalListItemDTO]:
    proposals = get_available_proposal_queryset(user)

    return [
        build_proposal_list_item_dto(proposal)
        for proposal in proposals
    ]


def list_dailyplan_proposals(
    user,
    dailyplan_id: int,
) -> list[NutritionProposalListItemDTO]:
    proposals = (
        get_available_proposal_queryset(user)
        .filter(dailyplan_id=dailyplan_id)
    )

    return [
        build_proposal_list_item_dto(proposal)
        for proposal in proposals
    ]


def search_proposals(
    user,
    query: str,
) -> list[NutritionProposalListItemDTO]:
    query = (query or "").strip()

    proposals = get_available_proposal_queryset(user)

    if query:
        proposals = proposals.filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(dailyplan__name__icontains=query)
        )

    return [
        build_proposal_list_item_dto(proposal)
        for proposal in proposals
    ]


def get_proposal_detail(
    user,
    proposal_id: int,
) -> NutritionProposalDTO:
    proposal = get_object_or_404(
        get_available_proposal_queryset(user),
        pk=proposal_id,
    )

    return build_proposal_dto(proposal)