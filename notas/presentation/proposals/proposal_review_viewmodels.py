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
class ProposalReviewFoodVM:
    food_id: int | None
    food_name: str
    quantity: float | None
    unit: str
    protein: float | None
    carbs: float | None
    fat: float | None
    total_kcal: float | None

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ProposalReviewKpisVM:
    total_kcal: float | None
    protein: float | None
    carbs: float | None
    fat: float | None
    ppk: float | None
    alloc_protein: float | None
    alloc_carbs: float | None
    alloc_fat: float | None

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ProposalReviewMealVM:
    name: str
    foods: list[ProposalReviewFoodVM]
    kpis: ProposalReviewKpisVM | None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "foods": [
                food.as_dict()
                for food in self.foods
            ],
            "kpis": self.kpis.as_dict() if self.kpis else None,
        }


@dataclass(frozen=True)
class ProposalReviewDailyPlanMealVM:
    hour: str | None
    note: str
    meal: ProposalReviewMealVM

    def as_dict(self) -> dict:
        return {
            "hour": self.hour,
            "note": self.note,
            "meal": self.meal.as_dict(),
        }


@dataclass(frozen=True)
class ProposalReviewDailyPlanVM:
    name: str
    meals: list[ProposalReviewDailyPlanMealVM]
    kpis: ProposalReviewKpisVM | None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "meals": [
                meal.as_dict()
                for meal in self.meals
            ],
            "kpis": self.kpis.as_dict() if self.kpis else None,
        }


@dataclass(frozen=True)
class ProposalReviewPayloadVM:
    intent: str | None
    is_create_meal: bool
    is_create_dailyplan: bool
    proposed_payload: dict[str, Any]
    simulation: dict[str, Any] | None
    targets: dict[str, Any]
    meal: ProposalReviewMealVM | None
    dailyplan: ProposalReviewDailyPlanVM | None

    def as_dict(self) -> dict:
        return {
            "intent": self.intent,
            "is_create_meal": self.is_create_meal,
            "is_create_dailyplan": self.is_create_dailyplan,
            "proposed_payload": self.proposed_payload,
            "simulation": self.simulation,
            "targets": self.targets,
            "meal": self.meal.as_dict() if self.meal else None,
            "dailyplan": self.dailyplan.as_dict() if self.dailyplan else None,
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
            meal=_build_meal_review_vm(
                intent=intent,
                simulation=simulation,
            ),
            dailyplan=_build_dailyplan_review_vm(
                intent=intent,
                simulation=simulation,
            ),
        ),
    )


def _build_meal_review_vm(
    intent: str | None,
    simulation: dict[str, Any] | None,
) -> ProposalReviewMealVM | None:
    if intent != CREATE_MEAL_INTENT:
        return None

    if not isinstance(simulation, dict):
        return None

    meal = simulation.get("meal")

    if not isinstance(meal, dict):
        return None

    return _build_meal_from_simulation(meal)


def _build_dailyplan_review_vm(
    intent: str | None,
    simulation: dict[str, Any] | None,
) -> ProposalReviewDailyPlanVM | None:
    if intent != CREATE_DAILYPLAN_INTENT:
        return None

    if not isinstance(simulation, dict):
        return None

    dailyplan = simulation.get("dailyplan")

    if not isinstance(dailyplan, dict):
        return None

    return ProposalReviewDailyPlanVM(
        name=_safe_str(dailyplan.get("name")),
        meals=[
            _build_dailyplan_meal_review_vm(meal_payload)
            for meal_payload in _safe_list(dailyplan.get("meals"))
            if isinstance(meal_payload, dict)
        ],
        kpis=_build_kpis_review_vm(
            _safe_dict(dailyplan.get("kpis")),
        ),
    )


def _build_dailyplan_meal_review_vm(
    payload: dict[str, Any],
) -> ProposalReviewDailyPlanMealVM:
    return ProposalReviewDailyPlanMealVM(
        hour=_safe_optional_str(payload.get("hour")),
        note=_safe_str(payload.get("note")),
        meal=_build_meal_from_simulation(
            _safe_dict(payload.get("meal")),
        ),
    )


def _build_meal_from_simulation(
    meal: dict[str, Any],
) -> ProposalReviewMealVM:
    return ProposalReviewMealVM(
        name=_safe_str(meal.get("name")),
        foods=[
            _build_food_review_vm(food)
            for food in _safe_list(meal.get("foods"))
            if isinstance(food, dict)
        ],
        kpis=_build_kpis_review_vm(
            _safe_dict(meal.get("kpis")),
        ),
    )


def _build_food_review_vm(
    food: dict[str, Any],
) -> ProposalReviewFoodVM:
    return ProposalReviewFoodVM(
        food_id=_safe_int_or_none(food.get("food_id")),
        food_name=_safe_str(food.get("food_name")),
        quantity=_safe_float_or_none(food.get("quantity")),
        unit=_safe_str(food.get("unit"), default="g"),
        protein=_safe_float_or_none(food.get("protein")),
        carbs=_safe_float_or_none(food.get("carbs")),
        fat=_safe_float_or_none(food.get("fat")),
        total_kcal=_safe_float_or_none(food.get("total_kcal")),
    )


def _build_kpis_review_vm(
    kpis: dict[str, Any],
) -> ProposalReviewKpisVM | None:
    if not kpis:
        return None

    return ProposalReviewKpisVM(
        total_kcal=_safe_float_or_none(kpis.get("total_kcal")),
        protein=_safe_float_or_none(kpis.get("protein")),
        carbs=_safe_float_or_none(kpis.get("carbs")),
        fat=_safe_float_or_none(kpis.get("fat")),
        ppk=_safe_float_or_none(kpis.get("ppk")),
        alloc_protein=_safe_float_or_none(kpis.get("alloc_protein")),
        alloc_carbs=_safe_float_or_none(kpis.get("alloc_carbs")),
        alloc_fat=_safe_float_or_none(kpis.get("alloc_fat")),
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


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value

    return []


def _safe_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value

    if value is None:
        return default

    return str(value)


def _safe_optional_str(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None

    return str(value)


def _safe_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    return None


def _safe_float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int | float):
        return float(value)

    return None