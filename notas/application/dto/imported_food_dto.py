from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ImportedFoodDTO:
    source: str
    source_food_id: str
    source_dataset: str
    source_version: str

    name: str
    canonical_name: str

    protein: Decimal
    carbs: Decimal
    fat: Decimal

    food_group: str = ""
    food_subgroup: str = ""

    fiber_g_per_100g: Decimal | None = None
    sugar_g_per_100g: Decimal | None = None
    saturated_fat_g_per_100g: Decimal | None = None
    sodium_mg_per_100g: Decimal | None = None

    license_name: str = ""
    attribution: str = ""
    source_url: str = ""
    raw_payload_hash: str = ""
    normalized_payload_hash: str = ""