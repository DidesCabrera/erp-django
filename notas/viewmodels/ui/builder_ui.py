from notas.viewmodels.base_vm import UI
from notas.navigation.breadcrumb_builder import build_breadcrumb
from notas.navigation.registry import NAVIGATION_STRUCTURE

def build_ui_vm(viewmode, instance=None, parents=None):

    breadcrumb = build_breadcrumb(
        entity=viewmode.entity,
        subgroup=viewmode.scope,
        parents=parents,
        instance=instance,
    )

    nav_root = resolve_navigation_root(viewmode.entity)

    nav_config = NAVIGATION_STRUCTURE.get(nav_root, {})
    icon = nav_config.get("icon")

    section_label = nav_config.get("section", {}).get("label")

    return UI(
        viewmode=str(viewmode),
        entity=viewmode.entity,
        mode=viewmode.mode,
        scope=viewmode.scope,
        nav_root=nav_root,
        icon=icon,
        breadcrumb=breadcrumb,
        section_label=section_label,
    )


def resolve_navigation_root(entity: str) -> str:
    config = NAVIGATION_STRUCTURE.get(entity)

    if not config:
        return entity

    if "navigation_root" in config:
        return config["navigation_root"]

    return entity