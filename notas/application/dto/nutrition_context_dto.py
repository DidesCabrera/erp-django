from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class UserNutritionContextDTO:
    user_id: int
    username: str
    current_weight: float | None
    has_current_weight: bool

    def as_dict(self) -> dict:
        return asdict(self)