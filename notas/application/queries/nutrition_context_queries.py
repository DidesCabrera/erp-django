from notas.application.dto.nutrition_context_dto import (
    UserNutritionContextDTO,
)
from notas.application.services.nutrition.weight import get_current_weight


def get_user_nutrition_context(user) -> UserNutritionContextDTO:
    current_weight = get_current_weight(user)

    current_weight_value = (
        float(current_weight)
        if current_weight is not None
        else None
    )

    return UserNutritionContextDTO(
        user_id=user.id,
        username=user.username,
        current_weight=current_weight_value,
        has_current_weight=current_weight_value is not None,
    )