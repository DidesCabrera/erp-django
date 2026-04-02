from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class NavItemSpec:
    key: str
    label: str
    icon: str
    url_name: str
    nav_root: str
    scope: Optional[str] = None
    page_icon: Optional[str] = None


@dataclass(frozen=True)
class NavGroupSpec:
    key: str
    label: str
    icon: str
    items: tuple[NavItemSpec, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NavSectionSpec:
    key: str
    label: str
    groups: tuple[NavGroupSpec, ...] = field(default_factory=tuple)


APP_NAVIGATION = (
    NavSectionSpec(
        key="workspace",
        label="Workspace",
        groups=(
            NavGroupSpec(
                key="library",
                label="Mi Librería",
                icon="bookmark",
                items=(
                    NavItemSpec(
                        key="dailyplan_personal",
                        label="Mis Planes Diarios",
                        icon="clipboard-list",
                        page_icon="bookmark",
                        url_name="dailyplan_list",
                        nav_root="dailyplan",
                        scope="personal",
                    ),
                    NavItemSpec(
                        key="meal_personal",
                        label="Mis Comidas",
                        icon="salad",
                        page_icon="bookmark",
                        url_name="meal_list",
                        nav_root="meal",
                        scope="personal",
                    ),
                    NavItemSpec(
                        key="food_personal",
                        label="Mis Alimentos",
                        icon="carrot",
                        page_icon="bookmark",
                        url_name="food_list",
                        nav_root="food",
                        scope="personal",
                    ),
                ),
            ),
            NavGroupSpec(
                key="create",
                label="Crear",
                icon="circle-fading-plus",
                items=(
                    NavItemSpec(
                        key="dailyplan_create",
                        label="Nuevo Plan",
                        icon="clipboard-list",
                        page_icon="circle-fading-plus",
                        url_name="dailyplan_create",
                        nav_root="dailyplan",
                        scope="create",
                    ),
                    NavItemSpec(
                        key="meal_create",
                        label="Nueva Comida",
                        icon="salad",
                        page_icon="circle-fading-plus",
                        url_name="meal_create",
                        nav_root="meal",
                        scope="create",
                    ),
                    NavItemSpec(
                        key="food_create",
                        label="Nuevo Alimento",
                        icon="carrot",
                        page_icon="circle-fading-plus",
                        url_name="food_create",
                        nav_root="food",
                        scope="create",
                    ),
                    NavItemSpec(
                        key="food_import",
                        label="Importar Alimentos",
                        icon="file-down",
                        page_icon="file-down",
                        url_name="import_foods",
                        nav_root="food",
                        scope="import",
                    ),
                ),
            ),
            NavGroupSpec(
                key="drafts",
                label="Borradores",
                icon="pencil",
                items=(
                    NavItemSpec(
                        key="dailyplan_draft",
                        label="Planes Diarios",
                        icon="clipboard-list",
                        page_icon="pencil",
                        url_name="dailyplan_draft_list",
                        nav_root="dailyplan",
                        scope="draft",
                    ),
                    NavItemSpec(
                        key="meal_draft",
                        label="Comidas",
                        icon="salad",
                        page_icon="pencil",
                        url_name="meal_draft_list",
                        nav_root="meal",
                        scope="draft",
                    ),
                ),
            ),
            NavGroupSpec(
                key="explore",
                label="Explorar",
                icon="search",
                items=(
                    NavItemSpec(
                        key="dailyplan_explore",
                        label="Explorar Planes",
                        icon="clipboard-list",
                        page_icon="search",
                        url_name="dailyplan_explore_list",
                        nav_root="dailyplan",
                        scope="explore",
                    ),
                    NavItemSpec(
                        key="meal_explore",
                        label="Explorar Comidas",
                        icon="salad",
                        page_icon="search",
                        url_name="meal_explore_list",
                        nav_root="meal",
                        scope="explore",
                    ),
                ),
            ),
        ),
    ),
    NavSectionSpec(
        key="account",
        label="Cuenta",
        groups=(
            NavGroupSpec(
                key="profile",
                label="Perfil",
                icon="circle-user-round",
                items=(
                    NavItemSpec(
                        key="profile_detail",
                        label="Mi Perfil",
                        icon="circle-user-round",
                        page_icon="circle-user-round",
                        url_name="profile_detail",
                        nav_root="profile",
                        scope="personal",
                    ),
                ),
            ),
        ),
    ),
)