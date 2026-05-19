import re
from dataclasses import dataclass

from notas.application.services.food_imports.localized_names import (
    FoodLocalizedNameInput,
    ensure_food_localized_names,
)
from notas.domain.models import Food, FoodLocalizedName, FoodSourceMetadata


@dataclass(frozen=True)
class ApplyUSDASpanishDisplayNamesResult:
    matched_foods: int
    created_localized_names: int
    updated_localized_names: int
    skipped_localized_names: int


EXACT_DISPLAY_NAME_TRANSLATIONS = {
    "oats, raw": "Avena",
    "chicken breast, cooked": "Pechuga de pollo cocida",
    "eggs, grade a, large, egg whole": "Huevo entero",
    "rice, white, long grain, unenriched, raw": "Arroz blanco crudo",
    "rice, brown, long grain, unenriched, raw": "Arroz integral crudo",
    "nuts, almonds, whole, raw": "Almendras crudas",
    "kale, raw": "Kale crudo",
    "hummus, commercial": "Hummus",
}


EXACT_PART_TRANSLATIONS = {
    "raw": "crudo",
    "cooked": "cocido",
    "dry": "seco",
    "dried": "seco",
    "frozen": "congelado",
    "canned": "enlatado",
    "fresh": "fresco",
    "commercial": "comercial",
    "restaurant": "restaurante",
    "prepared": "preparado",
    "unheated": "sin calentar",
    "heated in oven": "calentado en horno",
    "ready-to-serve": "listo para servir",
    "with salt added": "con sal añadida",
    "without salt": "sin sal",
    "unsweetened": "sin azúcar",
    "sweetened": "endulzado",
    "plain": "natural",
    "nonfat": "sin grasa",
    "lowfat": "bajo en grasa",
    "whole": "entero",
    "whole grain": "grano entero",
    "old fashioned": "tradicional",
    "steel cut": "cortada",
    "large": "grande",
    "grade a": "grado A",
    "white": "blanco",
    "brown": "integral",
    "black": "negro",
    "red": "rojo",
    "green": "verde",
    "yellow": "amarillo",
    "drained solids": "sólidos drenados",
    "drained and rinsed": "drenado y enjuagado",
    "regular pack": "envase regular",
    "vitamin d fortified": "fortificado con vitamina D",
    "with added vitamin c": "con vitamina C añadida",
    "from concentrate": "desde concentrado",
    "shelf stable": "estable a temperatura ambiente",
    "refrigerated": "refrigerado",
    "wild caught": "capturado silvestre",
    "farm raised": "de cultivo",
    "boneless": "sin hueso",
    "skinless": "sin piel",
    "with skin": "con piel",
    "without skin": "sin piel",
    "meat only": "solo carne",
    "meat and skin": "carne y piel",
    "lean only": "solo magro",
    "separable lean only": "solo magro separable",
    "separable lean and fat": "magro y grasa separables",
    "trimmed to 0\" fat": "recortado a 0 pulgadas de grasa",
    "trimmed to 1/8\" fat": "recortado a 1/8 pulgadas de grasa",
    "ground": "molido",
    "sliced": "laminado",
    "diced": "en cubos",
    "grated": "rallado",
    "peeled": "pelado",
    "seeded": "sin semillas",
    "seedless": "sin semillas",
    "breaded": "apanado",
    "fried": "frito",
    "pan-fried": "frito en sartén",
    "par fried": "prefrito",
    "boiled": "hervido",
    "braised": "braseado",
    "roasted": "tostado",
    "dry roasted": "tostado seco",
    "pasteurized": "pasteurizado",
    "low moisture": "baja humedad",
    "part-skim": "parcialmente descremado",
    "full fat": "entero",
    "defatted": "desgrasado",
    "all-purpose": "todo uso",
    "enriched": "enriquecido",
    "unenriched": "no enriquecido",
    "bleached": "blanqueado",
    "unbleached": "sin blanquear",
    "fluid": "líquido",
    "solid": "sólido",
    "mild": "suave",
    "light": "liviano",
}


PHRASE_TRANSLATIONS = {
    "grape tomatoes": "tomates uva",
    "tomatoes": "tomates",
    "tomato": "tomate",
    "snap beans": "porotos verdes",
    "green beans": "porotos verdes",
    "beans": "porotos",
    "frankfurter": "salchicha",
    "beef": "vacuno",
    "nuts": "frutos secos",
    "almonds": "almendras",
    "almond": "almendra",
    "eggplant": "berenjena",
    "egg white": "clara de huevo",
    "egg yolk": "yema de huevo",
    "egg whole": "huevo entero",
    "eggs": "huevos",
    "egg": "huevo",
    "onion rings": "aros de cebolla",
    "onions": "cebollas",
    "onion": "cebolla",
    "pickles": "pepinillos",
    "cucumber": "pepino",
    "cheese": "queso",
    "parmesan": "parmesano",
    "cheddar": "cheddar",
    "cottage": "cottage",
    "mozzarella": "mozzarella",
    "american": "americano",
    "grapefruit juice": "jugo de pomelo",
    "orange juice": "jugo de naranja",
    "apple juice": "jugo de manzana",
    "juice": "jugo",
    "peaches": "duraznos",
    "nectarines": "nectarines",
    "kiwifruit": "kiwi",
    "sunflower seed kernels": "semillas de maravilla peladas",
    "sunflower": "maravilla",
    "seeds": "semillas",
    "mustard": "mostaza",
    "yogurt": "yogur",
    "greek": "griego",
    "strawberry": "frutilla",
    "oil": "aceite",
    "coconut": "coco",
    "chicken breast": "pechuga de pollo",
    "chicken thigh": "trutro de pollo",
    "chicken wing": "ala de pollo",
    "chicken drumstick": "trutro corto de pollo",
    "chicken": "pollo",
    "fish": "pescado",
    "tuna": "atún",
    "halibut": "halibut",
    "haddock": "eglefino",
    "pollock": "abadejo",
    "salmon": "salmón",
    "pork belly": "panceta de cerdo",
    "pork chop": "chuleta de cerdo",
    "pork loin": "lomo de cerdo",
    "pork": "cerdo",
    "ham": "jamón",
    "sausage": "longaniza",
    "chorizo": "chorizo",
    "bacon": "tocino",
    "lamb": "cordero",
    "bison": "bisonte",
    "turkey": "pavo",
    "rice": "arroz",
    "wild rice": "arroz salvaje",
    "fried rice": "arroz frito",
    "flour": "harina",
    "wheat": "trigo",
    "whole wheat": "trigo integral",
    "bread": "pan",
    "corn": "maíz",
    "soy": "soya",
    "oat": "avena",
    "oats": "avena",
    "potato": "papa",
    "potatoes": "papas",
    "sweet potato": "camote",
    "carrots": "zanahorias",
    "carrot": "zanahoria",
    "mushroom": "champiñón",
    "mushrooms": "champiñones",
    "lettuce": "lechuga",
    "cabbage": "repollo",
    "kale": "kale",
    "spinach": "espinaca",
    "squash": "zapallo",
    "peppers": "pimientos",
    "bell pepper": "pimentón",
    "plantains": "plátanos",
    "bananas": "plátanos",
    "banana": "plátano",
    "apples": "manzanas",
    "apple": "manzana",
    "sauce": "salsa",
    "pasta sauce": "salsa para pasta",
    "spaghetti": "espagueti",
    "marinara": "marinara",
    "cookies": "galletas",
    "oatmeal": "avena",
    "raisins": "pasas",
    "olives": "aceitunas",
    "pimiento": "pimiento",
    "milk": "leche",
    "butter": "mantequilla",
    "cream": "crema",
    "water": "agua",
    "sodium": "sodio",
    "salt": "sal",
    "sugar": "azúcar",
    "protein": "proteína",
    "fiber": "fibra",
    "kidney": "riñón",
    "navy": "blanco",
    "pinto": "pinto",
    "cannellini": "cannellini",
    "black": "negro",
    "red kidney": "riñón rojo",
    "drumstick": "trutro corto",
    "thigh": "trutro",
    "wing": "ala",
    "breast": "pechuga",
}


WORD_TRANSLATIONS = {
    "or": "o",
    "and": "y",
    "with": "con",
    "without": "sin",
    "in": "en",
    "from": "de",
    "to": "a",
    "not": "no",
    "a": "A",
    "raw": "crudo",
    "dry": "seco",
    "dried": "seco",
    "cooked": "cocido",
    "frozen": "congelado",
    "canned": "enlatado",
    "white": "blanco",
    "brown": "integral",
    "red": "rojo",
    "green": "verde",
    "yellow": "amarillo",
    "black": "negro",
    "whole": "entero",
    "large": "grande",
    "small": "pequeño",
    "light": "liviano",
    "plain": "natural",
    "fresh": "fresco",
    "commercial": "comercial",
    "restaurant": "restaurante",
    "flour": "harina",
    "beans": "porotos",
    "cheese": "queso",
    "chicken": "pollo",
    "fish": "pescado",
    "pork": "cerdo",
    "beef": "vacuno",
    "rice": "arroz",
    "egg": "huevo",
    "eggs": "huevos",
    "nuts": "frutos secos",
    "almonds": "almendras",
    "kale": "kale",
    "hummus": "hummus",
    "oil": "aceite",
    "juice": "jugo",
    "milk": "leche",
    "yogurt": "yogur",
    "sauce": "salsa",
    "seeds": "semillas",
    "tomatoes": "tomates",
    "tomato": "tomate",
    "onions": "cebollas",
    "onion": "cebolla",
    "potatoes": "papas",
    "potato": "papa",
    "apples": "manzanas",
    "apple": "manzana",
}


def translate_usda_food_name_to_spanish(name: str) -> str:
    """
    Translate a USDA display name into an operational Spanish display name.

    This is intentionally deterministic and glossary-based. It is not meant to
    be a perfect natural-language translation layer; it gives My Scoope a
    stable Spanish display name for imported USDA foods that can later be
    curated manually.
    """

    cleaned_name = _clean_text(name)

    if not cleaned_name:
        return ""

    exact_key = _normalize_translation_key(cleaned_name)

    if exact_key in EXACT_DISPLAY_NAME_TRANSLATIONS:
        return EXACT_DISPLAY_NAME_TRANSLATIONS[exact_key]

    translated_parts = [
        _translate_part(part)
        for part in cleaned_name.split(",")
    ]

    return _clean_text(", ".join(part for part in translated_parts if part))


def apply_usda_spanish_display_names_to_foods(
    *,
    foods,
) -> ApplyUSDASpanishDisplayNamesResult:
    matched_foods = 0
    created_localized_names = 0
    updated_localized_names = 0
    skipped_localized_names = 0

    for food in foods:
        matched_foods += 1

        if _has_primary_spanish_localized_name(food):
            skipped_localized_names += 1
            continue

        display_name = translate_usda_food_name_to_spanish(food.name)

        if not display_name:
            skipped_localized_names += 1
            continue

        result = ensure_food_localized_names(
            food=food,
            localized_names=[
                FoodLocalizedNameInput(
                    name=display_name,
                    language="es",
                    country="CL",
                    is_primary=True,
                ),
            ],
        )

        created_localized_names += result.created_count
        updated_localized_names += result.updated_count
        skipped_localized_names += result.skipped_count

    return ApplyUSDASpanishDisplayNamesResult(
        matched_foods=matched_foods,
        created_localized_names=created_localized_names,
        updated_localized_names=updated_localized_names,
        skipped_localized_names=skipped_localized_names,
    )


def apply_usda_spanish_display_names_to_visible_global_foods() -> ApplyUSDASpanishDisplayNamesResult:
    foods = (
        Food.objects
        .filter(
            is_global=True,
            is_active=True,
            visibility__in=[
                Food.VISIBILITY_CORE,
                Food.VISIBILITY_EXTENDED,
            ],
            source_metadata__source=FoodSourceMetadata.SOURCE_USDA,
        )
        .prefetch_related("localized_names")
        .order_by("id")
    )

    return apply_usda_spanish_display_names_to_foods(
        foods=foods,
    )


def _has_primary_spanish_localized_name(food: Food) -> bool:
    prefetched_localized_names = getattr(
        food,
        "_prefetched_objects_cache",
        {},
    ).get("localized_names")

    if prefetched_localized_names is not None:
        localized_names = prefetched_localized_names
    else:
        localized_names = food.localized_names.all()

    return any(
        localized_name.language == "es"
        and localized_name.country == "CL"
        and localized_name.is_primary
        for localized_name in localized_names
    )


def _translate_part(part: str) -> str:
    normalized_part = _normalize_translation_key(part)

    if not normalized_part:
        return ""

    if normalized_part in EXACT_PART_TRANSLATIONS:
        return EXACT_PART_TRANSLATIONS[normalized_part]

    translated = normalized_part

    for source, target in _sorted_phrase_translations():
        translated = _replace_phrase(translated, source, target)

    words = [
        WORD_TRANSLATIONS.get(word, word)
        for word in translated.split()
    ]

    return _capitalize_display_part(" ".join(words))


def _sorted_phrase_translations() -> list[tuple[str, str]]:
    return sorted(
        PHRASE_TRANSLATIONS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )


def _replace_phrase(text: str, source: str, target: str) -> str:
    pattern = r"\b" + re.escape(source) + r"\b"

    return re.sub(pattern, target, text)


def _capitalize_display_part(value: str) -> str:
    value = _clean_text(value)

    if not value:
        return ""

    return value[0].upper() + value[1:]


def _normalize_translation_key(value: str) -> str:
    value = _clean_text(value).lower()
    value = value.replace("/", " ")
    value = value.replace("(", " ")
    value = value.replace(")", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _clean_text(value: str | None) -> str:
    if value is None:
        return ""

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    return value