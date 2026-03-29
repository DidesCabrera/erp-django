from notas.presentation.viewmodels.base_vm import UI
from notas.presentation.navigation.breadcrumb_builder import build_breadcrumb
from notas.presentation.navigation.registry import NAVIGATION_STRUCTURE


def resolve_navigation_root(entity: str) -> str:
    config = NAVIGATION_STRUCTURE.get(entity)

    if not config:
        return entity

    if "navigation_root" in config:
        return config["navigation_root"]

    return entity


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

    subgroups = nav_config.get("subgroups", {})

    page_icon = None

    if viewmode.scope and viewmode.scope in subgroups:
        page_icon = subgroups[viewmode.scope].get("page-icon")

    if not page_icon:
        page_icon = nav_config.get("section", {}).get("page-icon")

    title = breadcrumb[-1].label if breadcrumb else ""
    root = breadcrumb[-2].label if breadcrumb else ""

    is_inside = viewmode.mode != "list"

    back_url = None

    if len(breadcrumb) >= 2:
        back_url = breadcrumb[-2].url

    return UI(
        viewmode=str(viewmode),
        entity=viewmode.entity,
        mode=viewmode.mode,
        scope=viewmode.scope,
        nav_root=nav_root,
        icon=icon,
        page_icon=page_icon,
        breadcrumb=breadcrumb,
        section_label=section_label,
        title=title,
        root=root,
        is_inside=is_inside,
        back_url=back_url
    )