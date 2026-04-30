from django.db.models import Q
from django.shortcuts import get_object_or_404

from notas.application.dto.food_dto import (
    FoodDTO,
    FoodListItemDTO,
    FoodMacroDTO,
)
from notas.domain.models import Food


def build_food_macro_dto(food: Food) -> FoodMacroDTO:
    alloc = food.alloc

    return FoodMacroDTO(
        protein=float(food.protein),
        carbs=float(food.carbs),
        fat=float(food.fat),
        total_kcal=float(food.total_kcal),
        kcal_protein=float(food.kcal_protein),
        kcal_carbs=float(food.kcal_carbs),
        kcal_fat=float(food.kcal_fat),
        alloc_protein=float(alloc["protein"]),
        alloc_carbs=float(alloc["carbs"]),
        alloc_fat=float(alloc["fat"]),
    )


def build_food_list_item_dto(food: Food) -> FoodListItemDTO:
    return FoodListItemDTO(
        id=food.id,
        name=food.name,
        category=food.category,
        created_by_id=food.created_by_id,
        macros=build_food_macro_dto(food),
    )


def build_food_dto(food: Food) -> FoodDTO:
    return FoodDTO(
        id=food.id,
        name=food.name,
        category=food.category,
        created_by_id=food.created_by_id,
        macros=build_food_macro_dto(food),
    )


def get_available_food_queryset(user):
    """
    Foods visibles para el usuario en esta etapa:
    - alimentos creados por el usuario;
    - alimentos de sistema, con created_by=None.

    Si más adelante Food tiene is_public/shared, este es el punto donde
    se amplía la regla de lectura.
    """
    return (
        Food.objects
        .filter(
            Q(created_by=user) |
            Q(created_by__isnull=True)
        )
        .order_by("name", "id")
    )


def list_user_foods(user) -> list[FoodListItemDTO]:
    foods = (
        Food.objects
        .filter(created_by=user)
        .order_by("name", "id")
    )

    return [
        build_food_list_item_dto(food)
        for food in foods
    ]


def list_available_foods(user) -> list[FoodListItemDTO]:
    foods = get_available_food_queryset(user)

    return [
        build_food_list_item_dto(food)
        for food in foods
    ]


def search_foods(user, query: str) -> list[FoodListItemDTO]:
    clean_query = (query or "").strip()

    foods = get_available_food_queryset(user)

    if clean_query:
        foods = foods.filter(
            name__icontains=clean_query,
        )

    return [
        build_food_list_item_dto(food)
        for food in foods
    ]


def get_food_detail(user, food_id: int) -> FoodDTO:
    food = get_object_or_404(
        get_available_food_queryset(user),
        pk=food_id,
    )

    return build_food_dto(food)