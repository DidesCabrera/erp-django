import json
from pathlib import Path
from typing import Any


class FoundationFoodsReaderError(ValueError):
    """Raised when a Foundation Foods JSON file cannot be read safely."""


FOUNDATION_FOODS_ROOT_KEYS = (
    "FoundationFoods",
    "foundationFoods",
    "foundation_foods",
    "foods",
    "FoodData",
    "foodData",
)


def read_foundation_food_payloads_from_json(path: str | Path) -> list[dict[str, Any]]:
    """
    Read USDA Foundation Foods payloads from a local JSON file.

    The official downloadable files may be consumed in two controlled shapes:
    - a direct list of food payloads
    - an object containing the food list under a known dataset root key

    This reader does not map, validate nutrients, or write to the database.
    It only isolates file parsing and root-shape handling from management commands.
    """

    json_path = Path(path)

    try:
        with json_path.open("r", encoding="utf-8") as file:
            raw_payload = json.load(file)
    except json.JSONDecodeError as exc:
        raise FoundationFoodsReaderError(f"Invalid JSON file: {exc}") from exc
    except OSError as exc:
        raise FoundationFoodsReaderError(f"Could not read JSON file: {exc}") from exc

    food_payloads = extract_foundation_food_payloads(raw_payload)

    return food_payloads


def extract_foundation_food_payloads(raw_payload: Any) -> list[dict[str, Any]]:
    """
    Extract Foundation Foods records from a decoded JSON payload.

    Keeping this function separate makes the command easy to test without
    touching the filesystem and keeps future CSV/ZIP readers independent.
    """

    if isinstance(raw_payload, list):
        return _ensure_payload_list(raw_payload)

    if isinstance(raw_payload, dict):
        for root_key in FOUNDATION_FOODS_ROOT_KEYS:
            candidate = raw_payload.get(root_key)

            if candidate is not None:
                return _ensure_payload_list(candidate, root_key=root_key)

        available_keys = ", ".join(sorted(str(key) for key in raw_payload.keys()))
        raise FoundationFoodsReaderError(
            "JSON root object does not contain a supported Foundation Foods list. "
            f"Supported keys: {', '.join(FOUNDATION_FOODS_ROOT_KEYS)}. "
            f"Available keys: {available_keys or '(none)'}"
        )

    raise FoundationFoodsReaderError(
        "JSON root must be either a list of USDA food payloads or an object "
        "containing a supported Foundation Foods list."
    )


def _ensure_payload_list(
    candidate: Any,
    *,
    root_key: str | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(candidate, list):
        location = f"JSON root key '{root_key}'" if root_key else "JSON root"
        raise FoundationFoodsReaderError(f"{location} must contain a list of food payloads.")

    invalid_indexes = [
        index
        for index, item in enumerate(candidate)
        if not isinstance(item, dict)
    ]

    if invalid_indexes:
        preview = ", ".join(str(index) for index in invalid_indexes[:5])
        suffix = "" if len(invalid_indexes) <= 5 else ", ..."
        location = f" under root key '{root_key}'" if root_key else ""
        raise FoundationFoodsReaderError(
            f"Foundation Foods list{location} must contain only objects. "
            f"Invalid indexes: {preview}{suffix}"
        )

    return candidate