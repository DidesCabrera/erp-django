from dataclasses import dataclass

from django.db import transaction

from notas.domain.models import Food


@dataclass(frozen=True)
class FoodCreateResult:
    food: Food


@dataclass(frozen=True)
class FoodUpdateResult:
    food: Food

@dataclass(frozen=True)
class FoodBulkCreateResult:
    foods: list[Food]

    @property
    def created_count(self) -> int:
        return len(self.foods)


@transaction.atomic
def create_food(
    *,
    user,
    name,
    protein,
    carbs,
    fat,
) -> FoodCreateResult:
    food = Food.objects.create(
        name=(name or "").strip(),
        protein=protein,
        carbs=carbs,
        fat=fat,
        created_by=user,
    )

    return FoodCreateResult(
        food=food,
    )


@transaction.atomic
def update_food(
    *,
    food: Food,
    name,
    protein,
    carbs,
    fat,
) -> FoodUpdateResult:
    food.name = (name or "").strip()
    food.protein = protein
    food.carbs = carbs
    food.fat = fat

    food.save(
        update_fields=[
            "name",
            "protein",
            "carbs",
            "fat",
        ]
    )

    return FoodUpdateResult(
        food=food,
    )

@transaction.atomic
def bulk_create_foods(
    *,
    user,
    rows,
) -> FoodBulkCreateResult:
    foods = []

    for row in rows:
        food = Food.objects.create(
            name=(row["name"] or "").strip(),
            protein=row["protein"],
            carbs=row["carbs"],
            fat=row["fat"],
            created_by=user,
        )
        foods.append(food)

    return FoodBulkCreateResult(
        foods=foods,
    )