from dataclasses import dataclass
from typing import Any

from notas.application.dto.proposal_payloads import (
    CREATE_DAILYPLAN_INTENT,
    CREATE_MEAL_INTENT,
    ProposedDailyPlanPayloadDTO,
    ProposedMealPayloadDTO,
    parse_proposal_payload,
)


@dataclass(frozen=True)
class ProposalPayloadValidationErrorDTO:
    code: str
    message: str
    field: str | None = None

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "field": self.field,
        }


@dataclass(frozen=True)
class ProposalPayloadValidationResultDTO:
    is_valid: bool
    intent: str | None
    errors: list[ProposalPayloadValidationErrorDTO]
    parsed_payload: ProposedMealPayloadDTO | ProposedDailyPlanPayloadDTO | None = None

    def as_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "intent": self.intent,
            "errors": [
                error.as_dict()
                for error in self.errors
            ],
            "parsed_payload": (
                self.parsed_payload.as_dict()
                if self.parsed_payload is not None
                else None
            ),
        }


ERROR_MESSAGES = {
    "proposal_payload_must_be_object": "Proposal payload must be an object.",
    "unsupported_proposal_payload_intent": "Proposal payload intent is not supported.",
    "invalid_proposed_meal_payload_intent": "Meal proposal payload must use intent create_meal.",
    "invalid_proposed_dailyplan_payload_intent": "DailyPlan proposal payload must use intent create_dailyplan.",
    "proposed_meal_payload_must_be_object": "Meal proposal payload must be an object.",
    "proposed_dailyplan_payload_must_be_object": "DailyPlan proposal payload must be an object.",
    "proposed_food_item_payload_must_be_object": "Food item payload must be an object.",
    "proposed_meal_payload_meal_required": "Meal proposal payload requires a meal object.",
    "proposed_dailyplan_payload_dailyplan_required": "DailyPlan proposal payload requires a dailyplan object.",
    "proposed_meal_name_required": "Meal proposal requires a non-empty meal name.",
    "proposed_dailyplan_name_required": "DailyPlan proposal requires a non-empty dailyplan name.",
    "proposed_meal_foods_required": "Meal proposal requires a foods list.",
    "proposed_meal_foods_must_not_be_empty": "Meal proposal requires at least one food item.",
    "proposed_dailyplan_meals_required": "DailyPlan proposal requires a meals list.",
    "proposed_dailyplan_meals_must_not_be_empty": "DailyPlan proposal requires at least one meal.",
    "proposed_dailyplan_meals_exceeds_maximum": "DailyPlan proposal exceeds the maximum number of meals.",
    "proposed_dailyplan_meal_payload_must_be_object": "DailyPlan meal payload must be an object.",
    "proposed_dailyplan_meal_hour_must_be_string": "DailyPlan meal hour must be a string.",
    "proposed_dailyplan_meal_hour_must_use_hh_mm_format": "DailyPlan meal hour must use HH:MM format.",
    "proposed_dailyplan_meal_hour_out_of_range": "DailyPlan meal hour is out of range.",
    "proposed_dailyplan_meal_note_must_be_string": "DailyPlan meal note must be a string.",
    "proposed_dailyplan_meal_meal_required": "DailyPlan meal requires a nested meal object.",
    "proposed_dailyplan_meal_name_required": "DailyPlan meal requires a non-empty nested meal name.",
    "proposed_dailyplan_meal_foods_required": "DailyPlan meal requires a nested foods list.",
    "proposed_dailyplan_meal_foods_must_not_be_empty": "DailyPlan meal requires at least one nested food item.",
    "proposed_food_item_food_id_required": "Food item requires an integer food_id.",
    "proposed_food_item_quantity_required": "Food item requires a numeric quantity.",
    "proposed_food_item_quantity_must_be_positive": "Food item quantity must be positive.",
    "proposed_food_item_unit_required": "Food item requires a non-empty unit.",
}


FIELD_BY_ERROR_CODE = {
    "proposal_payload_must_be_object": None,
    "unsupported_proposal_payload_intent": "intent",
    "invalid_proposed_meal_payload_intent": "intent",
    "invalid_proposed_dailyplan_payload_intent": "intent",
    "proposed_meal_payload_meal_required": "meal",
    "proposed_dailyplan_payload_dailyplan_required": "dailyplan",
    "proposed_meal_name_required": "meal.name",
    "proposed_dailyplan_name_required": "dailyplan.name",
    "proposed_meal_foods_required": "meal.foods",
    "proposed_meal_foods_must_not_be_empty": "meal.foods",
    "proposed_dailyplan_meals_required": "dailyplan.meals",
    "proposed_dailyplan_meals_must_not_be_empty": "dailyplan.meals",
    "proposed_dailyplan_meals_exceeds_maximum": "dailyplan.meals",
    "proposed_dailyplan_meal_hour_must_be_string": "dailyplan.meals[].hour",
    "proposed_dailyplan_meal_hour_must_use_hh_mm_format": "dailyplan.meals[].hour",
    "proposed_dailyplan_meal_hour_out_of_range": "dailyplan.meals[].hour",
    "proposed_dailyplan_meal_note_must_be_string": "dailyplan.meals[].note",
    "proposed_dailyplan_meal_meal_required": "dailyplan.meals[].meal",
    "proposed_dailyplan_meal_name_required": "dailyplan.meals[].meal.name",
    "proposed_dailyplan_meal_foods_required": "dailyplan.meals[].meal.foods",
    "proposed_dailyplan_meal_foods_must_not_be_empty": "dailyplan.meals[].meal.foods",
    "proposed_food_item_payload_must_be_object": "foods[]",
    "proposed_food_item_food_id_required": "foods[].food_id",
    "proposed_food_item_quantity_required": "foods[].quantity",
    "proposed_food_item_quantity_must_be_positive": "foods[].quantity",
    "proposed_food_item_unit_required": "foods[].unit",
}


def validate_proposal_payload(
    payload: dict[str, Any],
) -> ProposalPayloadValidationResultDTO:
    intent = _extract_intent(payload)

    try:
        parsed_payload = parse_proposal_payload(payload)
    except ValueError as exc:
        error_code = str(exc)
        return ProposalPayloadValidationResultDTO(
            is_valid=False,
            intent=intent,
            errors=[
                _build_validation_error(error_code)
            ],
            parsed_payload=None,
        )

    return ProposalPayloadValidationResultDTO(
        is_valid=True,
        intent=parsed_payload.intent,
        errors=[],
        parsed_payload=parsed_payload,
    )


def validate_proposal_payload_or_raise(
    payload: dict[str, Any],
) -> ProposedMealPayloadDTO | ProposedDailyPlanPayloadDTO:
    result = validate_proposal_payload(payload)

    if result.is_valid and result.parsed_payload is not None:
        return result.parsed_payload

    first_error = result.errors[0] if result.errors else _build_validation_error(
        "unsupported_proposal_payload_intent"
    )

    raise ValueError(first_error.code)


def is_create_meal_payload(payload: dict[str, Any]) -> bool:
    return _extract_intent(payload) == CREATE_MEAL_INTENT


def is_create_dailyplan_payload(payload: dict[str, Any]) -> bool:
    return _extract_intent(payload) == CREATE_DAILYPLAN_INTENT


def _extract_intent(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None

    intent = payload.get("intent")

    if isinstance(intent, str):
        return intent

    return None


def _build_validation_error(code: str) -> ProposalPayloadValidationErrorDTO:
    return ProposalPayloadValidationErrorDTO(
        code=code,
        message=ERROR_MESSAGES.get(code, "Proposal payload is invalid."),
        field=FIELD_BY_ERROR_CODE.get(code),
    )