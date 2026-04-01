from django.urls import NoReverseMatch, reverse

from notas.presentation.navigation.app_registry import APP_SIDEBAR
from notas.presentation.navigation.registry import NAVIGATION_STRUCTURE


def resolve_navigation_root(entity: str) -> str:
    config = NAVIGATION_STRUCTURE.get(entity)

    if not config:
        return entity

    if "navigation_root" in config:
        return config["navigation_root"]

    return entity


def build_sidebar_vm(viewmode):
    current_nav_root = resolve_navigation_root(viewmode.entity)
    current_scope = viewmode.scope

    sections_vm = []

    for section in APP_SIDEBAR:
        section_vm = {
            "key": section.key,
            "label": section.label,
            "groups": [],
        }

        for group in section.groups:
            items_vm = []
            group_is_active = False

            for item in group.items:
                is_active = (
                    item.nav_root == current_nav_root
                    and item.scope == current_scope
                )

                if is_active:
                    group_is_active = True

                try:
                    url = reverse(item.url_name)
                except NoReverseMatch:
                    url = "#"

                items_vm.append(
                    {
                        "key": item.key,
                        "label": item.label,
                        "icon": item.icon,
                        "url": url,
                        "url_name": item.url_name,
                        "is_active": is_active,
                        "nav_root": item.nav_root,
                        "scope": item.scope,
                    }
                )

            section_vm["groups"].append(
                {
                    "key": group.key,
                    "label": group.label,
                    "icon": group.icon,
                    "is_active": group_is_active,
                    "items": items_vm,
                }
            )

        sections_vm.append(section_vm)

    return sections_vm
    