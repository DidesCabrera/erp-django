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
        "get_url": lambda dp, context=None: dailyplan_url(dp),
    },

    "explore_detail": {
        "label": "Ver",
        "method": "get",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_explore_detail", args=[dp.id]
        ),
    },

    "configure": {
        "label": "Configurar",
        "method": "get",
        "get_url": lambda dp, context=None: dailyplan_configure_url(dp),
        "capability": "can_edit_own_content",
    },

# FORK FAMILY ===================================

    "fork": {
        "label": "Duplicar",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

    "fork_explore": {
        "label": "Guardar en Personal",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

     "save": {
        "label": "Guardar",
        "method": "post",
        "get_url": lambda dp, ctx=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

    "save_my_list": {
        "label": "Guardar en Personal",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_fork", args=[dp.id]
        ),
        "capability": "can_fork",
    },

#____________________________________________

    "copy": {
        "label": "Copiar",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_copy", args=[dp.id]
        ),
        "capability": "can_copy",
    },


    "delete": {
        "label": "Borrar",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_delete", args=[dp.id]
        ),
        "capability": "is_admin",
    },

    "share": {
        "label": "Compartir",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_share", args=[dp.id]
        ),
    },

    "remove": {
        "label": "Remover",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_remove", args=[dp.id]
        ),
    },

    "unshare": {
        "label": "Quitar",
        "method": "post",
        "get_url": lambda share_id, context=None: reverse(
            "dailyplan_unshare", args=[share_id]
        ),
    },

    "edit": {
        "label": "Editar",
        "method": "post",
        "get_url": lambda dp, context=None: reverse(
            "dailyplan_edit", args=[dp.id]
        ),
    },

    "back_detail": {
        "label": "Finalizar",
        "method": "get",
        "get_url": lambda dp, context=None: dailyplan_url(dp),
    },

    "back_to_list": {
        "label": "Salir",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_list"
        ),
    },

    "back_to_explore_list": {
        "label": "Salir",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "dailyplan_explore_list"
        ),
    },

}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

DAILYPLAN_ACTIONS_BY_VIEWMODE = {
    
    # PERSONAL
    DAILYPLAN_VIEWMODE_LIST: [
        "detail",
        "share",
    ],

    DAILYPLAN_VIEWMODE_DETAIL: [
        "share",
        "fork",
        "edit",
        "remove",
        "back_to_list",
    ],

    # EXPLORE
    DAILYPLAN_VIEWMODE_EXPLORE_LIST: [
        "explore_detail",
        "save",
    ],

    DAILYPLAN_VIEWMODE_EXPLORE_DETAIL: [
        "fork_explore",
        "share",
        "back_to_explore_list"
    ],

    # SHARE
    DAILYPLAN_VIEWMODE_SHARED_LIST: [
        "detail",
        "save_my_list",
    ],

    DAILYPLAN_VIEWMODE_SHARED_DETAIL: [
        "save_my_list",
        "back_to_list",
    ],

    # DRAFT
    DAILYPLAN_VIEWMODE_DRAFT_LIST: [
        "detail",
        "edit",
        "remove",
    ],   

    # EDIT
    DAILYPLAN_VIEWMODE_EDIT: [
        "configure",
        "back_detail",
    ],

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
        })

    return actions
