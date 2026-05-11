from dataclasses import asdict, dataclass
from typing import Any


CREATE_MEAL_INTENT = "create_meal"
CREATE_DAILYPLAN_INTENT = "create_dailyplan"


@dataclass(frozen=True)
class ProposalReviewStatusVM:
    status: str
    is_reviewable: bool
    is_final: bool

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ProposalReviewPayloadVM:
    intent: str | None
    is_create_meal: bool
    is_create_dailyplan: bool
    proposed_payload: dict[str, Any]
    simulation: dict[str, Any] | None
    targets: dict[str, Any]

    def as_dict(self) -> dict:
        return {
            "intent": self.intent,
            "is_create_meal": self.is_create_meal,
            "is_create_dailyplan": self.is_create_dailyplan,
            "proposed_payload": self.proposed_payload,
            "simulation": self.simulation,
            "targets": self.targets,
        }


@dataclass(frozen=True)
class ProposalReviewVM:
    proposal_id: int
    title: str
    summary: str
    dailyplan_id: int | None
    dailyplan_name: str
    created_by_username: str | None
    reviewed_by_username: str | None
    status: ProposalReviewStatusVM
    payload: ProposalReviewPayloadVM

    def as_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "summary": self.summary,
            "dailyplan_id": self.dailyplan_id,
            "dailyplan_name": self.dailyplan_name,
            "created_by_username": self.created_by_username,
            "reviewed_by_username": self.reviewed_by_username,
            "status": self.status.as_dict(),
            "payload": self.payload.as_dict(),
        }


def build_proposal_review_vm(
    proposal: dict[str, Any],
) -> ProposalReviewVM:
    proposed_payload = _safe_dict(
        proposal.get("proposed_payload"),
    )
    validation_summary = _safe_dict(
        proposal.get("validation_summary"),
    )

    intent = _extract_intent(proposed_payload)
    simulation = _extract_simulation(validation_summary)

    return ProposalReviewVM(
        proposal_id=proposal.get("id"),
        title=proposal.get("title", ""),
        summary=proposal.get("summary", ""),
        dailyplan_id=proposal.get("dailyplan_id"),
        dailyplan_name=proposal.get("dailyplan_name", ""),
        created_by_username=proposal.get("created_by_username"),
        reviewed_by_username=proposal.get("reviewed_by_username"),
        status=ProposalReviewStatusVM(
            status=proposal.get("status", ""),
            is_reviewable=bool(proposal.get("is_reviewable")),
            is_final=bool(proposal.get("is_final")),
        ),
        payload=ProposalReviewPayloadVM(
            intent=intent,
            is_create_meal=intent == CREATE_MEAL_INTENT,
            is_create_dailyplan=intent == CREATE_DAILYPLAN_INTENT,
            proposed_payload=proposed_payload,
            simulation=simulation,
            targets=_safe_dict(proposal.get("targets")),
        ),
    )


def _extract_intent(
    proposed_payload: dict[str, Any],
) -> str | None:
    intent = proposed_payload.get("intent")

    if isinstance(intent, str) and intent.strip():
        return intent.strip()

    return None


def _extract_simulation(
    validation_summary: dict[str, Any],
) -> dict[str, Any] | None:
    simulation = validation_summary.get("simulation")

    if isinstance(simulation, dict):
        return simulation

    return None


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}