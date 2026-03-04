# navigation/registry.py

NAVIGATION_STRUCTURE = {
    "dailyplan": {
        "icon": "clipboard-list",
        "section": {
            "label": "Planes Diarios",
            "url_name": "dailyplan_list",
        },
        "subgroups": {
            "personal": {
                "label": "Mi Librería",
                "url_name": "dailyplan_list",
            },
            "explore": {
                "label": "Explorar",
                "url_name": "dailyplan_explore_list",
            },
            "shared": {
                "label": "Compartidos conmigo",
                "url_name": "dailyplan_shared_list",
            },
            "draft": {
                "label": "Borradores",
                "url_name": "dailyplan_draft_list",
            },
            "create": {
                "label": "Crear",
                "url_name": "dailyplan_create",
            }
        }
    },

    "meal": {
        "icon": "salad",
        "section": {
            "label": "Comidas",
            "url_name": "meal_list",
        },
        "subgroups": {
            "personal": {
                "label": "Mi Librería",
                "url_name": "meal_list",
            },
            "explore": {
                "label": "Explorar",
                "url_name": "meal_explore_list",
            },
            "shared": {
                "label": "Compartidos conmigo",
                "url_name": "meal_shared_list",
            },
            "draft": {
                "label": "Borradores",
                "url_name": "meal_draft_list",
            },
            "create": {
                "label": "Crear",
                "url_name": "meal_create",
            }
        }
    },

    # 🔹 Entidad secundaria (NO tiene section propia)
    "dailyplan_meal": {
        "navigation_root": "dailyplan"
    },
}


