from notas.presentation.config.viewmode import vm


PROFILE_VIEWMODE = vm("profile", "list", "personal")


# Food VIEWMODEs  ---------------------------------------------
FOOD_VIEWMODE_PERSONAL_LIST = vm("food", "list", "personal")
FOOD_VIEWMODE_PERSONAL_DETAIL = vm("food", "detail", "personal")
FOOD_VIEWMODE_PERSONAL_EDIT = vm("food", "edit", "personal")

FOOD_VIEWMODE_CREATE = vm("food", "list", "create")
FOOD_VIEWMODE_CONFIGURE = vm("food", "configure", "create")
FOOD_VIEWMODE_IMPORT = vm("food", "list", "import")

FOOD_VIEWMODE_MEAL = vm("food", "meal")

# MF VIEWMODE ---------------------------------------------
MEAL_FOOD_VIEWMODE_LIST = vm("meal_food", "list", "personal")
MEAL_FOOD_VIEWMODE_DETAIL = vm("meal_food", "detail", "personal")
MEAL_FOOD_VIEWMODE_PERSONAL_DEEP_EDIT = vm("meal_food", "deep_edit", "personal")
MEAL_FOOD_VIEWMODE_DRAFT_DEEP_EDIT = vm("meal_food", "deep_edit", "draft")

# Meal VIEWMODE ---------------------------------------------
MEAL_VIEWMODE_PERSONAL_LIST = vm("meal", "list", "personal")
MEAL_VIEWMODE_EXPLORE_LIST = vm("meal", "list", "explore")
MEAL_VIEWMODE_SHARED_LIST = vm("meal", "list", "shared")
MEAL_VIEWMODE_DRAFT_LIST = vm("meal", "list", "draft")

MEAL_VIEWMODE_PERSONAL_DETAIL = vm("meal", "detail", "personal")
MEAL_VIEWMODE_EXPLORE_DETAIL = vm("meal", "detail", "explore")
MEAL_VIEWMODE_SHARED_DETAIL = vm("meal", "detail", "shared")
MEAL_VIEWMODE_DRAFT_DETAIL = vm("meal", "detail", "draft")

MEAL_VIEWMODE_PERSONAL_EDIT = vm("meal", "edit", "personal")
MEAL_VIEWMODE_DRAFT_EDIT = vm("meal", "edit", "draft")

MEAL_VIEWMODE_CREATE = vm("meal", "list", "create")
MEAL_VIEWMODE_CONFIGURE = vm("meal", "configure", "personal")

MEAL_VIEWMODE_DAILYPLAN = vm("meal", "dailyplan")

MEAL_VIEWMODE_PERSONAL_EDIT_FROM_DAILYPLAN = vm("meal", "edit_from_dailyplan", "personal")


# DailyPlan VIEWMODE ---------------------------------------------
DAILYPLAN_VIEWMODE_PERSONAL_LIST = vm("dailyplan", "list", "personal")
DAILYPLAN_VIEWMODE_EXPLORE_LIST = vm("dailyplan", "list", "explore")
DAILYPLAN_VIEWMODE_SHARED_LIST = vm("dailyplan", "list", "shared")
DAILYPLAN_VIEWMODE_DRAFT_LIST = vm("dailyplan", "list", "draft")

DAILYPLAN_VIEWMODE_PERSONAL_DETAIL = vm("dailyplan", "detail", "personal")
DAILYPLAN_VIEWMODE_SHARED_DETAIL = vm("dailyplan", "detail", "shared")
DAILYPLAN_VIEWMODE_EXPLORE_DETAIL = vm("dailyplan", "detail", "explore")
DAILYPLAN_VIEWMODE_DRAFT_DETAIL = vm("dailyplan", "detail", "draft")

DAILYPLAN_VIEWMODE_PERSONAL_EDIT = vm("dailyplan", "edit", "personal")
DAILYPLAN_VIEWMODE_DRAFT_EDIT = vm("dailyplan", "edit", "draft")

DAILYPLAN_VIEWMODE_CREATE = vm("dailyplan", "list", "create")
DAILYPLAN_VIEWMODE_BUILD = vm("dailyplan", "build", "create")
DAILYPLAN_VIEWMODE_CONFIGURE = vm("dailyplan", "configure", "create")



# DPM VIEWMODE ---------------------------------------------
DAILYPLAN_MEAL_VIEWMODE_LIST = vm("dailyplan_meal", "list", "personal")
DAILYPLAN_MEAL_VIEWMODE_DETAIL = vm("dailyplan_meal", "detail", "personal")
DAILYPLAN_MEAL_VIEWMODE_PERSONAL_DEEP_EDIT = vm("dailyplan_meal", "deep_edit", "personal")
DAILYPLAN_MEAL_VIEWMODE_DRAFT_DEEP_EDIT = vm("dailyplan_meal", "deep_edit", "draft")

# DPM OTRO (PARA DEJAR PORCENTAJE DE ALLOC FUERA O DENTRO---------------------------------------------
ALLOC_PCT_OUTSIDE_THRESHOLD = 10

