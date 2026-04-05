# =========================
# DOMAIN NUTRITION SERVICES
# =========================

from notas.domain.constants.nutrition import (
    PROTEIN_KCAL_PER_GRAM,
    CARBS_KCAL_PER_GRAM,
    FAT_KCAL_PER_GRAM,
)


def kcal_from_macros(protein: float, carbs: float, fat: float) -> float:
    """
    Compute total kcal from macros.
    Pure function. No side effects.
    """
    return (
        protein * PROTEIN_KCAL_PER_GRAM
        + carbs * CARBS_KCAL_PER_GRAM
        + fat * FAT_KCAL_PER_GRAM
    )


def macro_kcal_breakdown(protein: float, carbs: float, fat: float) -> dict:
    """
    Returns kcal contribution per macro.
    """
    return {
        "kcal_protein": protein * PROTEIN_KCAL_PER_GRAM,
        "kcal_carbs": carbs * CARBS_KCAL_PER_GRAM,
        "kcal_fat": fat * FAT_KCAL_PER_GRAM,
    }


def macro_allocation(protein: float, carbs: float, fat: float) -> dict:
    """
    Returns percentage allocation of macros.
    """
    total = protein + carbs + fat

    if total == 0:
        return {
            "protein": 0,
            "carbs": 0,
            "fat": 0,
        }

    return {
        "protein": round((protein / total) * 100, 2),
        "carbs": round((carbs / total) * 100, 2),
        "fat": round((fat / total) * 100, 2),
    }