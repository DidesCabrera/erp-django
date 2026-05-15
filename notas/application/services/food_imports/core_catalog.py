INITIAL_CORE_FOOD_CANONICAL_NAMES = {
    "oats raw",
    "chicken breast cooked",
    "rice white cooked",
    "bananas raw",
}


def is_initial_core_food(canonical_name: str) -> bool:
    return canonical_name in INITIAL_CORE_FOOD_CANONICAL_NAMES