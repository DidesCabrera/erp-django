from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SidebarItemSpec:
    key: str
    label: str
    icon: str
    url_name: str
    nav_root: Optional[str] = None
    scope: Optional[str] = None


@dataclass(frozen=True)
class SidebarGroupSpec:
    key: str
    label: str
    icon: str
    items: tuple[SidebarItemSpec, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SidebarSectionSpec:
    key: str
    label: str
    groups: tuple[SidebarGroupSpec, ...] = field(default_factory=tuple)


APP_SIDEBAR = (
    SidebarSectionSpec(
        key="workspace",
        label="Workspace",
        groups=(
            SidebarGroupSpec(
                key="library",
                label="Mi Librería",
                icon="bookmark",
                items=(
                    SidebarItemSpec(
                        key="dailyplan_personal",
                        label="Mis Planes Diarios",
                        icon="clipboard-list",
                        url_name="dailyplan_list",
                        nav_root="dailyplan",
                        scope="personal",
                    ),
                    SidebarItemSpec(
                        key="meal_personal",
                        label="Mis Comidas",
                        icon="salad",
                        url_name="meal_list",
                        nav_root="meal",
                        scope="personal",
                    ),
                    SidebarItemSpec(
                        key="food_personal",
                        label="Mis Alimentos",
                        icon="carrot",
                        url_name="food_list",
                        nav_root="food",
                        scope="personal",
                    ),
                ),
            ),
            SidebarGroupSpec(
                key="create",
                label="Crear",
                icon="circle-fading-plus",
                items=(
                    SidebarItemSpec(
                        key="dailyplan_create",
                        label="Nuevo Plan",
                        icon="clipboard-list",
                        url_name="dailyplan_create",
                        nav_root="dailyplan",
                        scope="create",
                    ),
                    SidebarItemSpec(
                        key="meal_create",
                        label="Nueva Comida",
                        icon="salad",
                        url_name="meal_create",
                        nav_root="meal",
                        scope="create",
                    ),
                    SidebarItemSpec(
                        key="food_create",
                        label="Nuevo Alimento",
                        icon="carrot",
                        url_name="food_create",
                        nav_root="food",
                        scope="create",
                    ),
                    SidebarItemSpec(
                        key="food_import",
                        label="Importar Alimentos",
                        icon="file-down",
                        url_name="import_foods",
                        nav_root="food",
                        scope="import",
                    ),
                ),
            ),
            SidebarGroupSpec(
                key="drafts",
                label="Borradores",
                icon="pencil",
                items=(
                    SidebarItemSpec(
                        key="dailyplan_draft",
                        label="Planes Diarios",
                        icon="clipboard-list",
                        url_name="dailyplan_draft_list",
                        nav_root="dailyplan",
                        scope="draft",
                    ),
                    SidebarItemSpec(
                        key="meal_draft",
                        label="Comidas",
                        icon="salad",
                        url_name="meal_draft_list",
                        nav_root="meal",
                        scope="draft",
                    ),
                ),
            ),
            SidebarGroupSpec(
                key="explore",
                label="Explorar",
                icon="search",
                items=(
                    SidebarItemSpec(
                        key="dailyplan_explore",
                        label="Explorar Planes",
                        icon="clipboard-list",
                        url_name="dailyplan_explore_list",
                        nav_root="dailyplan",
                        scope="explore",
                    ),
                    SidebarItemSpec(
                        key="meal_explore",
                        label="Explorar Comidas",
                        icon="salad",
                        url_name="meal_explore_list",
                        nav_root="meal",
                        scope="explore",
                    ),
                ),
            ),
        ),
    ),
    SidebarSectionSpec(
        key="account",
        label="Cuenta",
        groups=(
            SidebarGroupSpec(
                key="profile",
                label="Perfil",
                icon="circle-user-round",
                items=(
                    SidebarItemSpec(
                        key="profile_detail",
                        label="Mi Perfil",
                        icon="circle-user-round",
                        url_name="profile_detail",
                        nav_root="profile",
                        scope="personal",
                    ),
                ),
            ),
        ),
    ),
)