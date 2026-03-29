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
                "page-icon": "bookmark",
                "label": "Mi Librería",
                "url_name": "dailyplan_list",
            },
            "explore": {
                "page-icon": "search",
                "label": "Explorar",
                "url_name": "dailyplan_explore_list",
            },
            "shared": {
                "page-icon": "user-plus",
                "label": "Compartidos conmigo",
                "url_name": "dailyplan_shared_list",
            },
            "draft": {
                "page-icon": "pencil",
                "label": "Borradores",
                "url_name": "dailyplan_draft_list",
            },
            "create": {
                "page-icon": "circle-fading-plus",
                "label": "Crear",
                "url_name": "dailyplan_create",
            }
        }
    },


    "meal": {
        "icon": "salad",
        "section": {
            "page-icon": "bookmark",
            "label": "Comidas",
            "url_name": "meal_list",
        },
        "subgroups": {
            "personal": {
                "page-icon": "bookmark",
                "label": "Mi Librería",
                "url_name": "meal_list",
            },
            "explore": {
                "page-icon": "search",
                "label": "Explorar",
                "url_name": "meal_explore_list",
            },
            "shared": {
                "page-icon": "user-plus",
                "label": "Compartidos conmigo",
                "url_name": "meal_shared_list",
            },
            "draft": {
                "page-icon": "pencil",
                "label": "Borradores",
                "url_name": "meal_draft_list",
            },
            "create": {
                "page-icon": "circle-fading-plus",
                "label": "Crear",
                "url_name": "meal_create",
            }
        }
    },

    # 🔹 Entidad secundaria (NO tiene section propia)
    "dailyplan_meal": {
        "navigation_root": "dailyplan"
    },


    "food": {
        "icon": "carrot",
        "section": {
            "label": "Alimentos",
            "url_name": "food_list",
        },
        "subgroups": {
            "personal": {
                "page-icon": "bookmark",
                "label": "General",
                "url_name": "food_list",
            },
            "create": {
                "page-icon": "circle-fading-plus",
                "label": "Crear",
                "url_name": "food_create",
            },
            "import": {
                "page-icon": "file-down",
                "label": "Importar",
                "url_name": "food_create",
            }
        }
    },
}


