from django.urls import reverse, NoReverseMatch

from notas.services.capabilities import get_capabilities
from notas.routing.meal import meal_url, meal_configure_url, meal_list_url
from notas.actions.constants import *

# ==================================================
# 1. DEFINICIÓN DECLARATIVA DE ACCIONES
# (qué es cada acción, NO cuándo aparece)
# ==================================================

MEAL_ACTION_DEFINITIONS = {
    "detail": {
        "label": "Ver",
        "method": "get",
        "get_url": lambda meal, context=None: meal_url(meal),
    },

    "explore_detail": {
        "label": "Ver",
        "method": "get",
        "get_url": lambda meal, context=None: reverse(
            "meal_explore_detail", args=[meal.id]
        ),
    },

    "cancel": {
        "label": "Cancelar",
        "method": "get",
        "get_url": lambda meal, context=None: meal_list_url(),
    },

    "configure": {
        "label": "Configurar",
        "method": "get",
        "get_url": lambda meal, context=None: meal_configure_url(meal),
        "capability": "can_edit_own_content",
    },

    "fork": {
        "label": "Duplicar",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_fork", args=[meal.id]
        ),
        "capability": "can_fork",
    },

    "copy": {
        "label": "Copy",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_copy", args=[meal.id]
        ),
        "capability": "can_copy",
    },

    "add_to_dailyplan": {
        "label": "Agregar a Plan",
        "method": "get",
        "get_url": lambda meal, context=None: reverse(
            "add_meal_from_list", args=[meal.id]
        ),
    },

    # ---- FUTURAS (safe no-op si no se usan) ----

    "delete": {
        "label": "Eliminar",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_delete", args=[meal.id]
        ),
    },

    "edit": {
        "label": "Editar",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_edit", args=[meal.id]
        ),
    },

    "deep_edit": {
        "label": "Editar",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_edit", args=[meal.id]
        ),
    },

    #se refiere a volver desde una edicion. reemplaza a save/cancel
    "back_detail": {
        "label": "Finalizar",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_detail", args=[meal.id]
        ),
    },

    "back_to_list": {
        "label": "Volver",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_list"
        ),
    },

    "back_to_explore_list": {
        "label": "Volver",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_explore_list"
        ),
    },

    "remove": {
        "label": "Remover",
        "method": "post",
        "get_url": lambda meal, ctx=None: reverse(
            "meal_remove", args=[meal.id]
        ),
    },

    "delete_draft": {
        "label": "Eliminar",
        "method": "post",
        "get_url": lambda meal, ctx=None: reverse(
            "meal_draft_delete", args=[meal.id]
        ),
    },

    "share": {
        "label": "Compartir",
        "method": "post",
        "get_url": lambda meal, context=None: reverse(
            "meal_share", args=[meal.id]
        ),
    }

}

# ==================================================
# 2. ACCIONES PERMITIDAS POR CONTEXTO
# ==================================================

MEAL_ACTIONS_BY_VIEWMODE = {
    MEAL_VIEWMODE_LIST: [
        "detail",
        "add_to_dailyplan",
        "share",
    ],

    MEAL_VIEWMODE_EXPLORE_LIST: [
        "explore_detail",
        "fork",
    ],

    MEAL_VIEWMODE_SHARED_LIST: [
        "detail",
        "save_my_list",
    ],

    MEAL_VIEWMODE_DRAFT_LIST: [
        "detail",
        "edit",
        "delete_draft",
    ],

    MEAL_VIEWMODE_SHARED_DETAIL: [
        "detail",
        "save_my_list",
        "unshare",
    ],


    MEAL_VIEWMODE_DETAIL: [
        "fork",
        "share",
        "add_to_dailyplan",
        "edit",
        "remove",
        "back_to_list",
    ],
    
    MEAL_VIEWMODE_EXPLORE_DETAIL: [
        "fork",
        "add_to_dailyplan",
         "back_to_explore_list",
    ],

    MEAL_VIEWMODE_CONFIGURE:[
        "back_detail",
    ],

    MEAL_VIEWMODE_EDIT: [
        "configure",
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

def resolve_meal_actions(meal, user, context=None):
    """
    Devuelve una lista de acciones disponibles para una Meal,
    según contexto + capabilities del usuario.
    """

    context = context or {}
    context_name = context.get("name")

    caps = get_capabilities(user)
    actions = []

    # --- acciones permitidas según contexto ---
    allowed_keys = MEAL_ACTIONS_BY_VIEWMODE.get(context_name, [])

    for key in allowed_keys:
        definition = MEAL_ACTION_DEFINITIONS.get(key)
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
            url = definition["get_url"](meal, context)
        except NoReverseMatch:
            continue

        actions.append({
            "key": key,
            "label": definition["label"],
            "url": url,
            "method": definition["method"],
        })

    return actions
