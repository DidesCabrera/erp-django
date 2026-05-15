from notas.application.services.food_imports.aliases import FoodAliasInput


USDA_SPANISH_ALIAS_CATALOG = {
    "oats raw": [
        FoodAliasInput(name="Avena", language="es", country="CL"),
        FoodAliasInput(name="Avena cruda", language="es", country="CL"),
        FoodAliasInput(name="Avena integral", language="es", country="CL"),
    ],
    "chicken breast cooked": [
        FoodAliasInput(name="Pechuga de pollo", language="es", country="CL"),
        FoodAliasInput(name="Pechuga de pollo cocida", language="es", country="CL"),
        FoodAliasInput(name="Pollo cocido", language="es", country="CL"),
    ],
    "rice white cooked": [
        FoodAliasInput(name="Arroz blanco", language="es", country="CL"),
        FoodAliasInput(name="Arroz blanco cocido", language="es", country="CL"),
        FoodAliasInput(name="Arroz cocido", language="es", country="CL"),
    ],
    "bananas raw": [
        FoodAliasInput(name="Plátano", language="es", country="CL"),
        FoodAliasInput(name="Banana", language="es", country="CL"),
        FoodAliasInput(name="Plátano crudo", language="es", country="CL"),
    ],
}