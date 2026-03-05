from dataclasses import dataclass


@dataclass
class FoodEditVM:
    id: int
    name: str
    protein: float
    carbs: float
    fat: float