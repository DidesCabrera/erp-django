from dataclasses import dataclass


@dataclass
class FoodListItemVM:
    id: int
    name: str
    protein: float
    carbs: float
    fat: float
    total_kcal: float
    alloc: object
    url: str
    actions: list


@dataclass
class FoodListVM:
    items: list