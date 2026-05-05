from notas.application.ai_tools.runtime import run_ai_tool
from notas.application.queries.validation_queries import (
    compare_dailyplan_to_targets,
)


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


def _compare_dailyplan_to_targets_data(
    user,
    dailyplan_id: int,
    targets: dict,
    tolerances: dict | None = None,
) -> dict:
    _ensure_targets_are_valid_for_tool(targets)
    _ensure_tolerances_are_valid_for_tool(tolerances)

    validation = compare_dailyplan_to_targets(
        user=user,
        dailyplan_id=dailyplan_id,
        targets=targets,
        tolerances=tolerances,
    ).as_dict()

    return {
        "validation": validation,
    }


def compare_dailyplan_to_targets_tool(
    user,
    dailyplan_id: int,
    targets: dict,
    tolerances: dict | None = None,
):
    return run_ai_tool(
        _compare_dailyplan_to_targets_data,
        user,
        dailyplan_id,
        targets,
        tolerances,
        user=user,
    )