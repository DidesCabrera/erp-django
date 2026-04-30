from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from notas.domain.models import DailyPlan, NutritionProposal


@dataclass(frozen=True)
class NutritionProposalCreateResult:
    proposal: NutritionProposal


@dataclass(frozen=True)
class NutritionProposalStatusResult:
    proposal: NutritionProposal


def _get_owned_dailyplan_for_proposal(
    *,
    user,
    dailyplan_id: int,
) -> DailyPlan:
    dailyplan = (
        DailyPlan.objects
        .filter(
            pk=dailyplan_id,
            created_by=user,
        )
        .first()
    )

    if not dailyplan:
        raise ValueError("dailyplan_not_available_for_proposal")

    return dailyplan


def _validate_initial_status(status: str) -> None:
    allowed_statuses = {
        NutritionProposal.STATUS_DRAFT,
        NutritionProposal.STATUS_PENDING_REVIEW,
    }

    if status not in allowed_statuses:
        raise ValueError("invalid_proposal_initial_status")


def _validate_source(source: str) -> None:
    allowed_sources = {
        NutritionProposal.SOURCE_MANUAL,
        NutritionProposal.SOURCE_AI,
        NutritionProposal.SOURCE_SYSTEM,
        NutritionProposal.SOURCE_MCP,
    }

    if source not in allowed_sources:
        raise ValueError("invalid_proposal_source")


def _ensure_can_review_proposal(
    *,
    user,
    proposal: NutritionProposal,
) -> None:
    if proposal.dailyplan.created_by_id != user.id:
        raise ValueError("proposal_review_not_allowed")


def _ensure_can_cancel_proposal(
    *,
    user,
    proposal: NutritionProposal,
) -> None:
    is_creator = proposal.created_by_id == user.id
    is_dailyplan_owner = proposal.dailyplan.created_by_id == user.id

    if not is_creator and not is_dailyplan_owner:
        raise ValueError("proposal_cancel_not_allowed")


def _ensure_pending_review(
    proposal: NutritionProposal,
) -> None:
    if proposal.status != NutritionProposal.STATUS_PENDING_REVIEW:
        raise ValueError("proposal_is_not_pending_review")


def _ensure_not_final(
    proposal: NutritionProposal,
) -> None:
    if proposal.is_final:
        raise ValueError("proposal_is_final")


@transaction.atomic
def create_dailyplan_proposal(
    *,
    user,
    dailyplan_id: int,
    title: str,
    summary: str = "",
    source: str = NutritionProposal.SOURCE_MANUAL,
    status: str = NutritionProposal.STATUS_PENDING_REVIEW,
    targets: dict | None = None,
    current_snapshot: dict | None = None,
    proposed_payload: dict | None = None,
    validation_summary: dict | None = None,
) -> NutritionProposalCreateResult:
    clean_title = (title or "").strip()
    clean_summary = (summary or "").strip()

    if not clean_title:
        raise ValueError("proposal_title_required")

    _validate_source(source)
    _validate_initial_status(status)

    dailyplan = _get_owned_dailyplan_for_proposal(
        user=user,
        dailyplan_id=dailyplan_id,
    )

    proposal = NutritionProposal.objects.create(
        dailyplan=dailyplan,
        created_by=user,
        status=status,
        source=source,
        title=clean_title,
        summary=clean_summary,
        targets=targets or {},
        current_snapshot=current_snapshot or {},
        proposed_payload=proposed_payload or {},
        validation_summary=validation_summary or {},
    )

    return NutritionProposalCreateResult(
        proposal=proposal,
    )


@transaction.atomic
def submit_proposal_for_review(
    *,
    user,
    proposal: NutritionProposal,
) -> NutritionProposalStatusResult:
    if proposal.created_by_id != user.id:
        raise ValueError("proposal_submit_not_allowed")

    if proposal.status != NutritionProposal.STATUS_DRAFT:
        raise ValueError("proposal_is_not_draft")

    proposal.status = NutritionProposal.STATUS_PENDING_REVIEW
    proposal.save(
        update_fields=[
            "status",
        ]
    )

    return NutritionProposalStatusResult(
        proposal=proposal,
    )


@transaction.atomic
def cancel_proposal(
    *,
    user,
    proposal: NutritionProposal,
) -> NutritionProposalStatusResult:
    _ensure_can_cancel_proposal(
        user=user,
        proposal=proposal,
    )
    _ensure_not_final(proposal)

    proposal.status = NutritionProposal.STATUS_CANCELLED
    proposal.reviewed_by = user
    proposal.reviewed_at = timezone.now()

    proposal.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    return NutritionProposalStatusResult(
        proposal=proposal,
    )


@transaction.atomic
def reject_proposal(
    *,
    user,
    proposal: NutritionProposal,
) -> NutritionProposalStatusResult:
    _ensure_can_review_proposal(
        user=user,
        proposal=proposal,
    )
    _ensure_pending_review(proposal)

    proposal.status = NutritionProposal.STATUS_REJECTED
    proposal.reviewed_by = user
    proposal.reviewed_at = timezone.now()

    proposal.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    return NutritionProposalStatusResult(
        proposal=proposal,
    )


@transaction.atomic
def approve_proposal(
    *,
    user,
    proposal: NutritionProposal,
) -> NutritionProposalStatusResult:
    """
    Aprueba la propuesta como estado revisado.

    Importante:
    este comando todavía NO aplica cambios al DailyPlan final.
    La aplicación del proposed_payload vendrá en una etapa posterior.
    """
    _ensure_can_review_proposal(
        user=user,
        proposal=proposal,
    )
    _ensure_pending_review(proposal)

    proposal.status = NutritionProposal.STATUS_APPROVED
    proposal.reviewed_by = user
    proposal.reviewed_at = timezone.now()

    proposal.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    return NutritionProposalStatusResult(
        proposal=proposal,
    )