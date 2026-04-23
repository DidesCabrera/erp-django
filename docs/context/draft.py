dailyplan



from django.urls import reverse, NoReverseMatch

from notas.application.services.access.capabilities import get_capabilities
from notas.interface.routing.dailyplan import dailyplan_url, dailyplan_configure_url
from notas.presentation.config.viewmodel_config import *

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# ==================================================

DAILYPLAN_ACTION_DEFINITIONS = {
    "detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda dp, context=None: dailyplan_url(dp),
    },

    "shared_detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_shared_detail", args=[dp.id]
        ),
    },
    
    "draft_detail": {
        "label": "Ver Draft",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_draft_detail", args=[dp.id]
        ),
    },

    "explore_detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_explore_detail", args=[dp.id]
        ),
    },

    "configure": {
        "label": "Configurar",
        "method": "get",
        "group": "overflow",
        "icon": "settings",
        "order": 90,
        "get_url": lambda dp, context=None: dailyplan_configure_url(dp),
        "capability": "can_access_distribution_settings",
    },

# FORK FAMILY ===================================

    "fork": {
        "label": "Duplicar",
        "method": "post",
        "group": "primary",
        "icon": "copy",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

    "fork_explore": {
        "label": "Guardar en Personal",
        "method": "post",
        "group": "primary",
        "icon": "bookmark",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

     "save": {
        "label": "Guardar",
        "method": "post",
        "group": "primary",
        "icon": "bookmark",
        "order": 90,
        "get_url": lambda dp, ctx=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

    "save_my_list": {
        "label": "Guardar en Personal",
        "method": "post",
        "group": "primary",
        "icon": "bookmark",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

#____________________________________________

    "copy": {
        "label": "Copiar",
        "method": "post",
        "group": "overflow",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_copy", args=[dp.id]
        ),
        "capability": "can_copy",
    },


    "delete": {
        "label": "Borrar",
        "method": "post",
        "group": "overflow",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_delete", args=[dp.id]
        ),
        "capability": "is_admin",
    },

    "share": {
        "label": "Compartir",
        "method": "post",
        "group": "overflow",
        "icon": "send",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_share", args=[dp.id]
        ),
    },

    "remove": {
        "label": "Remover",
        "method": "post",
        "group": "overflow",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_remove", args=[dp.id]
        ),
    },

    "unshare": {
        "label": "Quitar",
        "method": "post",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda share_id, context=None: reverse(
            "dailyplan_unshare", args=[share_id]
        ),
    },

    "edit": {
        "label": "Editar",
        "method": "post",
        "group": "overflow",
        "icon": "pencil",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_edit", args=[dp.id]
        ),
    },

    "draft_edit": {
        "label": "Retomar",
        "method": "post",
        "group": "primary",
        "icon": "pencil",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_draft_edit", args=[dp.id]
        ),
    },
    # Proveniente de un edit
    "back_detail": {
        "label": "Finalizar",
        "method": "get",
        "group": "primary",
        "icon": "check",
        "order": 90,
        "get_url": lambda dp, context=None: dailyplan_url(dp),
    },

    # Proveniente de un detail
    "back_to_list": {
        "label": "Volver",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "is_back": True,
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_list"
        ),
    },

    # Proveniente de un detail
    "back_to_explore_list": {
        "label": "Salir",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "is_back": True,
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_explore_list"
        ),
    },

    # Proveniente de un detail
    "back_to_shared_list": {
        "label": "Salir",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "is_back": True,
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_shared_list"
        ),
    },

    # Proveniente de un detail
    "back_to_draft_list": {
        "label": "Salir",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "is_back": True,
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_draft_list"
        ),
    },

}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

DAILYPLAN_ACTIONS_BY_VIEWMODE = {
    
    # PERSONAL
    DAILYPLAN_VIEWMODE_PERSONAL_LIST: [
        "fork",
        "detail",
        #"share",
    ],

    DAILYPLAN_VIEWMODE_PERSONAL_DETAIL: [
        "back_to_list",
        "configure",
        "fork",
        "remove",
    ],

    # EXPLORE
    DAILYPLAN_VIEWMODE_EXPLORE_LIST: [
        "save",
        "explore_detail",
    ],

    DAILYPLAN_VIEWMODE_EXPLORE_DETAIL: [
        "back_to_explore_list",
        "fork_explore",
    ],

    # SHARE
    DAILYPLAN_VIEWMODE_SHARED_LIST: [
        "save_my_list",
        "shared_detail",
    ],

    DAILYPLAN_VIEWMODE_SHARED_DETAIL: [
        "save_my_list",
        "unshare",
        "back_to_shared_list",
    ],

    # DRAFT
    DAILYPLAN_VIEWMODE_DRAFT_LIST: [
        "draft_edit",
        "remove",
    ],

    DAILYPLAN_VIEWMODE_DRAFT_DETAIL: [
        "draft_edit",
        "remove",
        "back_to_draft_list",
    ],  

    DAILYPLAN_VIEWMODE_DRAFT_EDIT: [
        "configure",
        "back_to_draft_list",
    ],

    DAILYPLAN_VIEWMODE_CONFIGURE: [
        "back_detail",
    ]

}





# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_dailyplan_actions(dailyplan, user, viewmode):
    """
    Devuelve una lista de acciones disponibles para un DailyPlan,
    según viewmode + capabilities del usuario.
    """

    caps = get_capabilities(user)
    actions = []

    allowed_keys = DAILYPLAN_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    for key in allowed_keys:
        definition = DAILYPLAN_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        capability_name = definition.get("capability")
        if capability_name:
            if not caps or not hasattr(caps, capability_name):
                continue
            if not getattr(caps, capability_name)():
                continue

        try:
            get_url = definition["get_url"]

            try:
                url = get_url(dailyplan, None)
            except TypeError:
                url = get_url(dailyplan)

        except NoReverseMatch:
            continue

        actions.append(
            {
                "key": key,
                "label": definition["label"],
                "url": url,
                "method": definition["method"],
                "group": definition.get("group", "primary"),
                "icon": definition.get("icon"),
                "order": definition.get("order", 100),
                "is_back": definition.get("is_back", False),
            }
        )

    return actions







meal


from django.urls import reverse, NoReverseMatch

from notas.application.services.access.capabilities import get_capabilities
from notas.interface.routing.meal import meal_url, meal_configure_url, meal_list_url
from notas.presentation.config.viewmodel_config import *

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# (qué es cada acción, NO cuándo aparece)
# ==================================================

MEAL_ACTION_DEFINITIONS = {
    "detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda meal, context=None: meal_url(meal),
    },

    "explore_detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_explore_detail", args=[meal.id]
        ),
    },

    "cancel": {
        "label": "Cancelar",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda meal, context=None: meal_list_url(),
    },

    "configure": {
        "label": "Configurar",
        "method": "get",
        "group": "overflow",
        "icon": "settings",
        "order": 90,
        "get_url": lambda meal, context=None: meal_configure_url(meal),
        "capability": "can_access_distribution_settings",
    },

    "fork": {
        "label": "Duplicar",
        "method": "post",
        "group": "overflow",
        "icon": "copy",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_fork", args=[meal.id]
        ),
        "capability": "can_fork",
    },

    "fork_explore": {
        "label": "Guardar en Personal",
        "method": "post",
        "group": "primary",
        "icon": "bookmark",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_fork", args=[meal.id]
        ),
        "capability": "can_fork",
    },

    "copy": {
        "label": "Copy",
        "method": "post",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_copy", args=[meal.id]
        ),
        "capability": "can_copy",
    },

    "add_to_dailyplan": {
        "label": "Agregar a Plan",
        "method": "get",
        "group": "overflow",
        "icon": "clipboard-plus",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "add_meal_from_list", args=[meal.id]
        ),
    },

    # ---- FUTURAS (safe no-op si no se usan) ----

    "delete": {
        "label": "Eliminar",
        "method": "post",
        "group": "overflow",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_delete", args=[meal.id]
        ),
    },


    "deep_edit": {
        "label": "Editar",
        "method": "post",
        "group": "primary",
        "icon": "pencil",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_detail", args=[meal.id]
        ),
    },

    #se refiere a volver desde una edicion. reemplaza a save/cancel
    "back_detail": {
        "label": "Finalizar",
        "method": "post",
        "group": "primary",
        "icon": "check",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_detail", args=[meal.id]
        ),
    },

    "finish_for_dailyplan": {
        "label": "Guardar y volver",
        "method": "post",
        "group": "primary",
        "icon": "check",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_detail", args=[meal.id]
        ),
    },

    "back_to_list": {
        "label": "Volver",
        "method": "post",
        "group": "overflow",
        "icon": "chevron-left",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_list"
        ),
    },

    "back_to_explore_list": {
        "label": "Volver",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_explore_list"
        ),
    },

    "remove": {
        "label": "Eliminar",
        "method": "post",
        "group": "overflow",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda meal, ctx=None: reverse(
            "meal_remove", args=[meal.id]
        ),
    },

    "delete_draft": {
        "label": "Eliminar",
        "method": "post",
        "group": "primary",
        "icon": "trash-2",
        "order": 90,
        "get_url": lambda meal, ctx=None: reverse(
            "meal_draft_delete", args=[meal.id]
        ),
    },

    "share": {
        "label": "Compartir",
        "method": "post",
        "group": "overflow",
        "icon": "send",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "meal_share", args=[meal.id]
        ),
    }

}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

MEAL_ACTIONS_BY_VIEWMODE = {
    MEAL_VIEWMODE_PERSONAL_LIST: [
        "add_to_dailyplan",
        "detail",
        #"share",
    ],


    MEAL_VIEWMODE_PERSONAL_DETAIL: [
        "back_to_list",
        "configure",
        "fork",
        "add_to_dailyplan",
        "remove",
    ],

    MEAL_VIEWMODE_EXPLORE_LIST: [
        "fork",
        "explore_detail",
    ],

    MEAL_VIEWMODE_SHARED_LIST: [
        "save_my_list",
        "detail",
    ],

    MEAL_VIEWMODE_DRAFT_LIST: [
        "delete_draft",
        "edit",
    ],

    MEAL_VIEWMODE_SHARED_DETAIL: [
        "save_my_list",
        "unshare",
    ],



    MEAL_VIEWMODE_PERSONAL_EDIT_FROM_DAILYPLAN: [
        "configure",
        "remove",
        "finish_for_dailyplan",
    ],
    
    MEAL_VIEWMODE_EXPLORE_DETAIL: [
        "back_to_explore_list",
        "fork",
    ],

    MEAL_VIEWMODE_CONFIGURE:[
        "back_detail",
    ],

    MEAL_VIEWMODE_CREATE: [
        "continue",
        "cancel",
    ],

    MEAL_VIEWMODE_DAILYPLAN: [
        # dentro de un dailyplan
        "detail",
    ],
}

# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_meal_actions(meal, user, viewmode):
    caps = get_capabilities(user)
    actions = []

    allowed_keys = MEAL_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    for key in allowed_keys:
        definition = MEAL_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        capability_name = definition.get("capability")
        if capability_name:
            if not caps or not hasattr(caps, capability_name):
                continue
            if not getattr(caps, capability_name)():
                continue

        try:
            get_url = definition["get_url"]

            try:
                url = get_url(meal, None)
            except TypeError:
                url = get_url(meal)

        except NoReverseMatch:
            continue

        actions.append(
            {
                "key": key,
                "label": definition["label"],
                "url": url,
                "method": definition["method"],
                "group": definition.get("group", "primary"),
                "icon": definition.get("icon"),
                "order": definition.get("order", 100),
                "is_back": definition.get("is_back", False),
            }
        )

    return actions
    """
    Devuelve una lista de acciones disponibles para una Meal
    según viewmode + capabilities.
    """
    caps = get_capabilities(user)
    actions = []

    allowed_keys = MEAL_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    for key in allowed_keys:

        definition = MEAL_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        # ------------------------------
        # capability check
        # ------------------------------

        capability_name = definition.get("capability")

        if capability_name:
            if not caps or not hasattr(caps, capability_name):
                continue

            if not getattr(caps, capability_name)():
                continue

        method = definition.get("method", "get")

        # ------------------------------
        # resolve URL (optional)
        # ------------------------------

        url = None
        get_url = definition.get("get_url")

        if get_url:
            try:
                url = get_url(meal, context)
            except NoReverseMatch:
                continue

        # ------------------------------
        # build action object
        # ------------------------------

        actions.append({
            "key": key,
            "label": definition["label"],
            "method": method,
            "url": url,
            "group": definition.get("group", "primary"),
            "icon": definition.get("icon"),
            "order": definition.get("order", 100),
        })

    return actions




    food


    from django.urls import reverse, NoReverseMatch
from notas.application.services.access.capabilities import get_capabilities
from notas.interface.routing.food import food_url, food_list_url
from notas.presentation.config.viewmodel_config import (
    FOOD_VIEWMODE_PERSONAL_LIST,
    FOOD_VIEWMODE_PERSONAL_DETAIL,
    FOOD_VIEWMODE_MEAL,
    FOOD_VIEWMODE_PERSONAL_EDIT,
)

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# (qué es cada acción, NO cuándo aparece)
# ==================================================

FOOD_ACTION_DEFINITIONS = {
    "detail": {
        "label": "View",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: food_url(food),
    },

    "cancel": {
        "label": "Cancel",
        "method": "get",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: food_list_url(),
    },

    # ---- FUTURAS (safe no-op si no se usan) ----

    "delete": {
        "label": "Delete",
        "method": "post",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: reverse(
            "food_delete", args=[food.id]
        ),
    },

    "edit": {
        "label": "Edit",
        "method": "post",
        "group": "primary",
        "icon": "pencil",
        "order": 90,
        "get_url": lambda food, context=None: reverse(
            "food_edit", args=[food.id]
        ),
    },

    "save": {
        "label": "Save",
        "method": "post",
        "group": "primary",
        "icon": "chevron-right",
        "order": 90,
        "get_url": lambda food, context=None: reverse(
            "food_detail", args=[food.id]
        ),
    },
}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

FOOD_ACTIONS_BY_VIEWMODE = {
    FOOD_VIEWMODE_PERSONAL_LIST: [
        "detail",
        "fork",
        "copy",
        "add_to_dailyplan",
    ],

    FOOD_VIEWMODE_PERSONAL_DETAIL: [
        "fork",
        "copy",
        "add_to_dailyplan",
        "edit",
        "delete",
    ],

    FOOD_VIEWMODE_PERSONAL_EDIT: [
        "save",
        "cancel",
    ],

    FOOD_VIEWMODE_MEAL: [
        # dentro de un dailyplan
        "detail",
    ],
}

# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_food_actions(food, user, viewmode):

    caps = get_capabilities(user)
    actions = []

    # --- acciones permitidas según contexto ---
    allowed_keys = FOOD_ACTIONS_BY_VIEWMODE.get(viewmode, [])

    for key in allowed_keys:
        definition = FOOD_ACTION_DEFINITIONS.get(key)
        if not definition:
            continue

        # --- capability check ---
        capability_name = definition.get("capability")
        if capability_name:
            if not caps or not hasattr(caps, capability_name):
                continue
            if not getattr(caps, capability_name)():
                continue

        # --- resolver URL (safe) ---
        try:
            get_url = definition["get_url"]
            try:
                url = get_url(food, None)
            except TypeError:
                url = get_url(food)
        except NoReverseMatch:
            continue

        actions.append({
            "key": key,
            "label": definition["label"],
            "url": url,
            "method": definition["method"],
            "group": definition.get("group", "primary"),
            "icon": definition.get("icon"),
            "order": definition.get("order", 100),
        })

    return actions
