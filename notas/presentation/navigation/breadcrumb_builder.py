# navigation/breadcrumb_builder.py
from typing import List, Optional, Iterable
from django.urls import reverse
from .registry import NAVIGATION_STRUCTURE
from notas.presentation.viewmodels.base_vm import BreadcrumbItem


def build_breadcrumb(
    *,
    entity: str,
    subgroup: Optional[str] = None,
    parents: Optional[Iterable[object]] = None,
    instance: Optional[object] = None,
) -> List[BreadcrumbItem]:

    breadcrumb: List[BreadcrumbItem] = []

    config = NAVIGATION_STRUCTURE.get(entity)
    if not config:
        return breadcrumb

    # 🔹 Resolver root navigation si existe
    if "navigation_root" in config:
        root_entity = config["navigation_root"]
        config = NAVIGATION_STRUCTURE.get(root_entity)

        if not config:
            return breadcrumb

    # 1️⃣ Sección principal
    section = config.get("section")
    if section:
        breadcrumb.append(
            BreadcrumbItem(
                label=section["label"],
                url=reverse(section["url_name"]),
            )
        )

    # 2️⃣ Subgrupo (scope)
    if subgroup:
        subgroups = config.get("subgroups", {})
        sub = subgroups.get(subgroup)

        if sub:
            breadcrumb.append(
                BreadcrumbItem(
                    label=sub["label"],
                    url=reverse(sub["url_name"]),
                )
            )

    # 3️⃣ Parents (jerarquía intermedia)
    if parents:
        for parent in parents:
            breadcrumb.append(
                BreadcrumbItem(
                    label=str(parent),
                    url=getattr(parent, "dailyplan_url", lambda: None)(),
                )
            )

    # 4 Instancia activa
    if instance:
        breadcrumb.append(
            BreadcrumbItem(
                label=str(instance),
                url=None,
            )
        )

    return breadcrumb