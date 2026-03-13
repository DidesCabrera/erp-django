from django.urls import reverse, NoReverseMatch

from notas.services.capabilities import get_capabilities
from notas.routing.dailyplan import dailyplan_url, dailyplan_configure_url
from notas.actions.constants import *

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# ==================================================

DAILYPLAN_ACTION_DEFINITIONS = {
    "detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "log-in",
        "order": 90,
        "get_url": lambda dp, context=None: dailyplan_url(dp),
    },

    "shared_detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "log-in",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_shared_detail", args=[dp.id]
        ),
    },
    
    "draft_detail": {
        "label": "Ver Draft",
        "method": "get",
        "group": "primary",
        "icon": "log-in",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_draft_detail", args=[dp.id]
        ),
    },

    "explore_detail": {
        "label": "Ver",
        "method": "get",
        "group": "primary",
        "icon": "log-in",
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
        "capability": "can_edit_own_content",
    },

# FORK FAMILY ===================================

    "fork": {
        "label": "Duplicar",
        "method": "post",
        "group": "overflow",
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
        "group": "primary",
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
        "group": "primary",
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
        "group": "primary",
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
        "group": "primary",
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

    "back_detail": {
        "label": "Finalizar",
        "method": "get",
        "group": "primary",
        "icon": "check",
        "order": 90,
        "get_url": lambda dp, context=None: dailyplan_url(dp),
    },

    "back_to_edit": {
        "label": "Volver",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_edit", args=[dp.id]
        ),
    },

    "back_to_list": {
        "label": "Salir",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_list"
        ),
    },

    "back_to_explore_list": {
        "label": "Salir",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_explore_list"
        ),
    },

    "back_to_shared_list": {
        "label": "Salir",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_shared_list"
        ),
    },

    "back_to_draft_list": {
        "label": "Salir",
        "method": "post",
        "group": "primary",
        "icon": "chevron-left",
        "order": 90,
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
        "detail",
        #"share",
    ],

    DAILYPLAN_VIEWMODE_PERSONAL_DETAIL: [
        #"share",
        "back_to_list",
        "edit",
        "fork",
    ],

    DAILYPLAN_VIEWMODE_PERSONAL_EDIT: [
        "back_detail",
        "configure",
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
        "back_to_edit",
    ]

}





# ==================================================
# 3. RESOLVER PRINCIPAL
# ==================================================

def resolve_dailyplan_actions(dailyplan, user, context=None):
    """
    Devuelve una lista de acciones disponibles para un DailyPlan,
    según contexto + capabilities del usuario.
    """

    context = context or {}
    context_name = context.get("name")

    caps = get_capabilities(user)
    actions = []

    allowed_keys = DAILYPLAN_ACTIONS_BY_VIEWMODE.get(context_name, [])

    for key in allowed_keys:
        definition = DAILYPLAN_ACTION_DEFINITIONS.get(key)
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
            url = definition["get_url"](dailyplan, context)
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
