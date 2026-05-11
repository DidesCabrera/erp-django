from notas.application.ai_tools.runtime import run_ai_tool
from notas.application.queries.proposal_queries import (
    get_proposal_detail,
    list_dailyplan_proposals,
    list_user_proposals,
    search_proposals,
)

from notas.application.services.commands.proposal_commands import (
    create_validated_dailyplan_build_proposal,
    create_validated_dailyplan_proposal,
    create_validated_meal_proposal,
)

from notas.domain.models import NutritionProposal




def _serialize_dto_list(items) -> list[dict]:
    return [
        item.as_dict()
        for item in items
    ]


def _ensure_payload_is_valid_for_tool(
    proposed_payload: dict | None,
) -> None:
    if proposed_payload is not None and not isinstance(proposed_payload, dict):
        raise ValueError("tool_proposed_payload_must_be_object")


def _ensure_targets_are_valid_for_tool(
    targets: dict,
) -> None:
    if not isinstance(targets, dict):
        raise ValueError("tool_targets_must_be_object")

    if not targets:
        raise ValueError("tool_targets_required")


def _ensure_tolerances_are_valid_for_tool(
    tolerances: dict | None,
) -> None:
    if tolerances is not None and not isinstance(tolerances, dict):
        raise ValueError("tool_tolerances_must_be_object")


def _ensure_title_is_valid_for_tool(
    title: str,
) -> None:
    if not isinstance(title, str):
        raise ValueError("tool_title_must_be_string")

    if not title.strip():
        raise ValueError("tool_title_required")


def _create_validated_dailyplan_proposal_data(
    user,
    dailyplan_id: int,
    title: str,
    targets: dict,
    proposed_payload: dict | None = None,
    tolerances: dict | None = None,
    summary: str = "",
) -> dict:
    _ensure_title_is_valid_for_tool(title)
    _ensure_targets_are_valid_for_tool(targets)
    _ensure_tolerances_are_valid_for_tool(tolerances)
    _ensure_payload_is_valid_for_tool(proposed_payload)

    result = create_validated_dailyplan_proposal(
        user=user,
        dailyplan_id=dailyplan_id,
        title=title,
        summary=summary,
        source=NutritionProposal.SOURCE_AI,
        targets=targets,
        tolerances=tolerances,
        proposed_payload=proposed_payload,
    )

    proposal = get_proposal_detail(
        user,
        result.proposal.id,
    ).as_dict()

    return {
        "proposal": proposal,
    }


def _create_validated_meal_proposal_data(
    user,
    dailyplan_id: int,
    title: str,
    proposed_payload: dict,
    targets: dict | None = None,
    summary: str = "",
) -> dict:
    _ensure_title_is_valid_for_tool(title)
    _ensure_payload_is_valid_for_tool(proposed_payload)

    result = create_validated_meal_proposal(
        user=user,
        dailyplan_id=dailyplan_id,
        title=title,
        summary=summary,
        source=NutritionProposal.SOURCE_AI,
        targets=targets or {},
        proposed_payload=proposed_payload,
    )

    proposal = get_proposal_detail(
        user,
        result.proposal.id,
    ).as_dict()

    return {
        "proposal": proposal,
    }
    

def _create_validated_dailyplan_build_proposal_data(
    user,
    dailyplan_id: int,
    title: str,
    proposed_payload: dict,
    targets: dict | None = None,
    summary: str = "",
) -> dict:
    _ensure_title_is_valid_for_tool(title)
    _ensure_payload_is_valid_for_tool(proposed_payload)

    result = create_validated_dailyplan_build_proposal(
        user=user,
        dailyplan_id=dailyplan_id,
        title=title,
        summary=summary,
        source=NutritionProposal.SOURCE_AI,
        targets=targets or {},
        proposed_payload=proposed_payload,
    )

    proposal = get_proposal_detail(
        user,
        result.proposal.id,
    ).as_dict()

    return {
        "proposal": proposal,
    }



def create_validated_meal_proposal_tool(
    user,
    dailyplan_id: int,
    title: str,
    proposed_payload: dict,
    targets: dict | None = None,
    summary: str = "",
):
    return run_ai_tool(
        _create_validated_meal_proposal_data,
        user,
        dailyplan_id,
        title,
        proposed_payload,
        targets,
        summary,
        user=user,
    )


def create_validated_dailyplan_build_proposal_tool(
    user,
    dailyplan_id: int,
    title: str,
    proposed_payload: dict,
    targets: dict | None = None,
    summary: str = "",
):
    return run_ai_tool(
        _create_validated_dailyplan_build_proposal_data,
        user,
        dailyplan_id,
        title,
        proposed_payload,
        targets,
        summary,
        user=user,
    )



def create_validated_dailyplan_proposal_tool(
    user,
    dailyplan_id: int,
    title: str,
    targets: dict,
    proposed_payload: dict | None = None,
    tolerances: dict | None = None,
    summary: str = "",
):
    return run_ai_tool(
        _create_validated_dailyplan_proposal_data,
        user,
        dailyplan_id,
        title,
        targets,
        proposed_payload,
        tolerances,
        summary,
        user=user,
    )


def _list_user_proposals_data(user) -> dict:
    return {
        "proposals": _serialize_dto_list(
            list_user_proposals(user),
        ),
    }


def list_user_proposals_tool(user):
    return run_ai_tool(
        _list_user_proposals_data,
        user,
        user=user,
    )


def _list_dailyplan_proposals_data(user, dailyplan_id: int) -> dict:
    return {
        "dailyplan_id": dailyplan_id,
        "proposals": _serialize_dto_list(
            list_dailyplan_proposals(
                user,
                dailyplan_id,
            ),
        ),
    }


def list_dailyplan_proposals_tool(user, dailyplan_id: int):
    return run_ai_tool(
        _list_dailyplan_proposals_data,
        user,
        dailyplan_id,
        user=user,
    )


def _search_proposals_data(user, query: str) -> dict:
    return {
        "proposals": _serialize_dto_list(
            search_proposals(
                user,
                query,
            ),
        ),
        "query": query,
    }


def search_proposals_tool(user, query: str):
    return run_ai_tool(
        _search_proposals_data,
        user,
        query,
        user=user,
    )


def _read_proposal_data(user, proposal_id: int) -> dict:
    return {
        "proposal": get_proposal_detail(
            user,
            proposal_id,
        ).as_dict(),
    }


def read_proposal_tool(user, proposal_id: int):
    return run_ai_tool(
        _read_proposal_data,
        user,
        proposal_id,
        user=user,
    )