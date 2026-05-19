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
        canonical_name="eggs grade a large egg whole",
        localized_names=[
            FoodLocalizedNameInput(
                name="Huevo entero",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Huevo", language="es", country="CL"),
            FoodAliasInput(name="Huevos", language="es", country="CL"),
            FoodAliasInput(name="Huevo entero", language="es", country="CL"),
            FoodAliasInput(name="Huevo grande", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="rice white long grain unenriched raw",
        localized_names=[
            FoodLocalizedNameInput(
                name="Arroz blanco crudo",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Arroz", language="es", country="CL"),
            FoodAliasInput(name="Arroz blanco", language="es", country="CL"),
            FoodAliasInput(name="Arroz blanco crudo", language="es", country="CL"),
            FoodAliasInput(name="Arroz crudo", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="rice brown long grain unenriched raw",
        localized_names=[
            FoodLocalizedNameInput(
                name="Arroz integral crudo",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Arroz integral", language="es", country="CL"),
            FoodAliasInput(name="Arroz integral crudo", language="es", country="CL"),
            FoodAliasInput(name="Arroz café", language="es", country="CL"),
            FoodAliasInput(name="Arroz cafe", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="nuts almonds whole raw",
        localized_names=[
            FoodLocalizedNameInput(
                name="Almendras crudas",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Almendra", language="es", country="CL"),
            FoodAliasInput(name="Almendras", language="es", country="CL"),
            FoodAliasInput(name="Almendras crudas", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="kale raw",
        localized_names=[
            FoodLocalizedNameInput(
                name="Kale crudo",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Kale", language="es", country="CL"),
            FoodAliasInput(name="Kale crudo", language="es", country="CL"),
            FoodAliasInput(name="Col rizada", language="es", country="CL"),
        ],
    ),
    CoreFoodSeedItem(
        canonical_name="hummus commercial",
        localized_names=[
            FoodLocalizedNameInput(
                name="Hummus",
                language="es",
                country="CL",
                is_primary=True,
            ),
        ],
        aliases=[
            FoodAliasInput(name="Hummus", language="es", country="CL"),
            FoodAliasInput(name="Humus", language="es", country="CL"),
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