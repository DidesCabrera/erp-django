from dataclasses import dataclass


@dataclass
class CategoryBadgeUI:
    label: str
    icon: str
    css: str


CATEGORY_BADGE_MAP = {
    "original": CategoryBadgeUI(
        label="Original",
        icon="user-round-pen",
        css="original",
    ),
    "duplicado": CategoryBadgeUI(
        label="Duplicado",
        icon="copy",
        css="duplicado",
    ),
    "en plan": CategoryBadgeUI(
        label="En plan",
        icon="calendar-fold",
        css="en-plan",
    ),
    "system": CategoryBadgeUI(
        label="Base",
        icon="database",
        css="system",
    ),
    "user": CategoryBadgeUI(
        label="Propio",
        icon="user",
        css="user",
    ),
}


def resolve_category_badge(category: str | None) -> CategoryBadgeUI | None:
    if not category:
        return None

    return CATEGORY_BADGE_MAP.get(
        category,
        CategoryBadgeUI(
            label=category.title(),
            icon="user-round-pen",
            css="default",
        ),
    )