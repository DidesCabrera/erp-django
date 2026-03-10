from dataclasses import dataclass, asdict
from typing import Optional


# =========================
# UI ATOMS
# =========================

@dataclass
class StructuralIndicatorsUI:
    meals_count: Optional[int] = None
    foods_count: Optional[int] = None
    

@dataclass
class TitleUI:
    name: str
    label: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    structural_indicators: Optional[StructuralIndicatorsUI] = None


@dataclass
class KPIUI:
    tot_kcal: float
    g_protein: float
    g_carbs: float
    g_fat: float
    kcal_protein: float
    kcal_carbs: float
    kcal_fat: float
    alloc_protein: float
    alloc_carbs: float
    alloc_fat: float


# =========================
# CARDS
# =========================

@dataclass
class MainCardUI:
    main_id: float
    titulo: TitleUI
    kpis: KPIUI

    # Presentation flags
    show_kpis: bool = False
    show_table: bool = False


# =========================
# ROOT VIEWMODEL
# =========================

@dataclass
class FoodDetailVM:

    header: dict
    main_card: MainCardUI

    def as_context(self):
        return {
            "ui": asdict(self)
        }
