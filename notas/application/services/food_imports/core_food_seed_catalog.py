from dataclasses import dataclass

from notas.application.services.food_imports.aliases import FoodAliasInput
from notas.application.services.food_imports.localized_names import (
    FoodLocalizedNameInput,
)


@dataclass(frozen=True)
class CoreFoodSeedItem:
    canonical_name: str
    localized_names: list[FoodLocalizedNameInput]
    aliases: list[FoodAliasInput]


CORE_FOOD_SEED_CATALOG = [
    CoreFoodSeedItem(
        canonical_name="oats raw",
        localized_names=[
            FoodLocalizedNameInput(
                name="Avena",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Avena", language="es", country="CL"),
            FoodAliasInput(name="Avena cruda", language="es", country="CL"),
            FoodAliasInput(name="Avena integral", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="chicken breast cooked",
        localized_names=[
            FoodLocalizedNameInput(
                name="Pechuga de pollo cocida",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Pollo", language="es", country="CL"),
            FoodAliasInput(name="Pechuga de pollo", language="es", country="CL"),
            FoodAliasInput(name="Pechuga de pollo cocida", language="es", country="CL"),
            FoodAliasInput(name="Pollo cocido", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="rice white cooked",
        localized_names=[
            FoodLocalizedNameInput(
                name="Arroz blanco cocido",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Arroz", language="es", country="CL"),
            FoodAliasInput(name="Arroz blanco", language="es", country="CL"),
            FoodAliasInput(name="Arroz blanco cocido", language="es", country="CL"),
            FoodAliasInput(name="Arroz cocido", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="bananas raw",
        localized_names=[
            FoodLocalizedNameInput(
                name="Plátano",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Plátano", language="es", country="CL"),
            FoodAliasInput(name="Platano", language="es", country="CL"),
            FoodAliasInput(name="Banana", language="es", country="CL"),
            FoodAliasInput(name="Plátano crudo", language="es", country="CL"),
        ],
    ),
]


def get_core_food_seed_by_canonical_name() -> dict[str, CoreFoodSeedItem]:
    return {
        item.canonical_name: item
        for item in CORE_FOOD_SEED_CATALOG
    }


def get_core_food_seed_canonical_names() -> set[str]:
    return {
        item.canonical_name
        for item in CORE_FOOD_SEED_CATALOG
    }