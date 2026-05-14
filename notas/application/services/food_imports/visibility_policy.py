from notas.domain.models import Food


def resolve_initial_food_visibility(*, quality_score: int) -> str:
    """
    Resolve the initial visibility for imported global foods.

    This is intentionally conservative:
    - high-quality records can become extended
    - imported records should not become core automatically
    - low-quality records should remain hidden
    - rejected is reserved for explicit curation decisions
    """

    if quality_score >= 70:
        return Food.VISIBILITY_EXTENDED

    return Food.VISIBILITY_HIDDEN